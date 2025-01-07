from enum import Enum
from collections import defaultdict, deque
from typing import Dict, Set, List, Optional

class TrustLevel(Enum):
    IMPLICIT = "implicit"      # Self
    COMPLETE = "complete"      # Fully-trusted introducer
    MARGINAL = "marginal"      # Key valid, but not fully-trusted
    PARTIAL = "partial"        # Single edge marking partial trust
    INVALID = "invalid"        # Not trusted

class PGPTrustWeb:
    def __init__(self):
        # Set of all known user names
        self.users: Set[str] = set()
        
        # direct_trust[A][B] = "complete" | "partial" if A signed B at that level
        # Example: direct_trust["alice"]["bob"] = "partial" means
        #          "alice partially trusts bob"
        self.direct_trust: Dict[str, Dict[str, str]] = defaultdict(dict)

    def add_node(self, name: str) -> bool:
        """
        Add a user to the web of trust. Returns False if already exists.
        Also sets user->user as IMPLICIT in direct_trust for convenience.
        """
        if name in self.users:
            return False
        self.users.add(name)
        # A user implicitly trusts themselves
        self.direct_trust[name][name] = TrustLevel.IMPLICIT.value
        return True

    def add_signature(self, signer: str, target: str, trust_level: str) -> dict:
        """
        signer signs target at trust_level ("complete" or "partial").
        Returns success/fail with message.
        """
        if signer not in self.users or target not in self.users:
            return {"success": False, "message": "One or both users don't exist"}
        
        if signer == target:
            return {"success": False, "message": "Cannot explicitly sign own key"}

        # Only allow "complete" or "partial" for direct edges
        if trust_level not in [TrustLevel.COMPLETE.value, TrustLevel.PARTIAL.value]:
            return {"success": False, "message": f"Invalid trust level: {trust_level}"}
        
        self.direct_trust[signer][target] = trust_level
        return {"success": True}

    # -------------------------------------------------------------------------
    # CORE LOGIC:  Determine overall trust (validity) from "viewer"'s perspective.
    # We'll do a multi-pass approach that is reminiscent of PGP's trust model:
    #
    # 1) A user is "IMPLICIT" valid if they are the viewer themselves.
    # 2) A user becomes "COMPLETE" valid if:
    #       - The viewer has a direct "complete" signature to them, OR
    #       - A "COMPLETE" valid user has a direct "complete" signature to them, etc. (chain)
    # 3) A user becomes "MARGINAL" valid if:
    #       - It has at least two partial signers, each of whom is themselves "valid"
    #         (either "COMPLETE" or "MARGINAL" or "IMPLICIT").
    # 4) By default, anything else is "INVALID".
    #
    # We iterate until no more changes occur (or do BFS in stages).
    # Then, once we have the final validity map, we can also gather "paths" that
    # use only valid signers.
    # -------------------------------------------------------------------------

    def compute_validity_map(self, viewer: str) -> Dict[str, TrustLevel]:
        """
        Compute and return a map:  user -> (IMPLICIT | COMPLETE | MARGINAL | INVALID)
        from the perspective of 'viewer'.
        """

        # Initialize everyone as INVALID from viewer's perspective
        validity_map = {u: TrustLevel.INVALID for u in self.users}
        
        if viewer not in self.users:
            # If the viewer doesn't exist in the web, everything stays INVALID
            return validity_map
        
        # The viewer implicitly trusts themselves
        validity_map[viewer] = TrustLevel.IMPLICIT
        
        # We will do repeated passes until stable
        changed = True
        while changed:
            changed = False

            for user in self.users:
                old_level = validity_map[user]

                # Skip if user is already complete or implicit,
                # because that's the highest forms of trust for a user.
                # (Implicit is not "higher" than complete, but we keep it as is.)
                if old_level in [TrustLevel.COMPLETE, TrustLevel.IMPLICIT]:
                    continue

                # 1) Check if any "COMPLETE" valid user (including the viewer) has a direct COMPLETE
                #    signature to 'user'. If so, user becomes COMPLETE valid.
                #    Also check if 'viewer' => 'user' is directly complete.
                if self.has_complete_endorsement(viewer, user, validity_map):
                    new_level = TrustLevel.COMPLETE
                else:
                    # 2) Otherwise, see if user can become MARGINAL:
                    #    Does user have >=2 partial signers who are themselves valid?
                    #    (valid means they are either IMPLICIT, COMPLETE, or MARGINAL)
                    partial_signers = self.count_valid_partial_signers(user, validity_map)
                    if partial_signers >= 2:
                        new_level = TrustLevel.MARGINAL
                    else:
                        # Otherwise user stays what it was or remains INVALID
                        new_level = old_level

                if new_level != old_level:
                    validity_map[user] = new_level
                    changed = True

        return validity_map

    def has_complete_endorsement(self, viewer: str, target: str,
                                 validity_map: Dict[str, TrustLevel]) -> bool:
        """
        Returns True if 'target' is signed with 'complete' trust by
        either 'viewer' itself, or ANY user who is 'COMPLETE' valid from 'viewer''s perspective.
        """
        # If the viewer itself has a direct COMPLETE signature to target, that's enough
        if (target in self.direct_trust[viewer] and
            self.direct_trust[viewer][target] == TrustLevel.COMPLETE.value):
            return True

        # Otherwise, check if there's *some* user 'X' who is "COMPLETE" valid
        # from viewer's perspective and 'X' has a direct COMPLETE signature on target.
        for x in self.users:
            if validity_map[x] == TrustLevel.COMPLETE:
                # x is fully trusted from viewer's perspective, so if x->target is complete
                # that means viewer also sees target as complete
                if (target in self.direct_trust[x] and
                    self.direct_trust[x][target] == TrustLevel.COMPLETE.value):
                    return True
        
        return False

    def count_valid_partial_signers(self, user: str,
                                    validity_map: Dict[str, TrustLevel]) -> int:
        """
        Count how many valid signers (IMPLICIT, COMPLETE, or MARGINAL) have a
        PARTIAL signature on 'user'.
        """
        count = 0
        for potential_signer in self.users:
            # Is potential_signer valid from viewer's perspective (implicit, complete, or marginal)?
            if validity_map[potential_signer] in [
                TrustLevel.IMPLICIT, TrustLevel.COMPLETE, TrustLevel.MARGINAL
            ]:
                # Does potential_signer->user exist and is it PARTIAL?
                if (user in self.direct_trust[potential_signer] and
                    self.direct_trust[potential_signer][user] == TrustLevel.PARTIAL.value):
                    count += 1
        return count

    # -------------------------------------------------------------------------
    # Once we know who is valid (and at which level) from the viewer's perspective,
    # we can collect actual "paths" that:
    #   - only traverse through users that are themselves valid
    #   - use edges that match the needed trust type (complete or partial).
    # For instance, to see if there's a "complete path" or "partial path."
    # -------------------------------------------------------------------------

    def _find_all_paths(self, viewer: str, target: str,
                        visited: List[str],
                        validity_map: Dict[str, TrustLevel],
                        edge_type_filter: Optional[str] = None) -> List[List[str]]:
        """
        Depth-first search for *all* paths from 'viewer' to 'target' that pass only
        through valid nodes (valid from the perspective of 'viewer') and optionally
        require each edge to be 'edge_type_filter' if specified
        (e.g. "complete" or "partial").
        """
        results = []

        # Mark the current node as visited
        visited.append(viewer)

        # If we reached 'target' (and it's not the trivial viewer==target case),
        # record the path.
        if viewer == target and len(visited) > 1:
            results.append(visited[:])
        else:
            # Explore neighbors
            for nxt in self.direct_trust[viewer]:
                # 1) 'nxt' must be "valid" from the viewer's perspective (IMPLICIT/COMPLETE/MARGINAL)
                if validity_map[nxt] not in [TrustLevel.IMPLICIT, TrustLevel.COMPLETE, TrustLevel.MARGINAL]:
                    continue
                
                # 2) If we're filtering by edge type, check that this edge matches
                if edge_type_filter is not None:
                    if self.direct_trust[viewer][nxt] != edge_type_filter:
                        continue

                # 3) Avoid cycles
                if nxt in visited:
                    continue

                # Recurse
                results += self._find_all_paths(nxt, target, visited[:],
                                                validity_map,
                                                edge_type_filter=edge_type_filter)
        return results

    def find_complete_paths(self, viewer: str, target: str,
                            validity_map: Dict[str, TrustLevel]) -> List[List[str]]:
        """
        Find all paths from viewer to target that use only 'complete' edges,
        and that go only through valid nodes.
        """
        return self._find_all_paths(
            viewer=viewer,
            target=target,
            visited=[],
            validity_map=validity_map,
            edge_type_filter=TrustLevel.COMPLETE.value
        )

    def find_partial_paths(self, viewer: str, target: str,
                           validity_map: Dict[str, TrustLevel]) -> List[List[str]]:
        """
        Find all paths from viewer to target that use only 'partial' edges,
        and that go only through valid nodes.
        """
        return self._find_all_paths(
            viewer=viewer,
            target=target,
            visited=[],
            validity_map=validity_map,
            edge_type_filter=TrustLevel.PARTIAL.value
        )

    # -------------------------------------------------------------------------
    # Public API: check_trust(viewer, target)
    # -------------------------------------------------------------------------
    def check_trust(self, viewer: str, target: str) -> dict:
        """
        Determines whether 'viewer' trusts 'target', and if so at what level.
        Also returns the relevant paths used to justify that trust.
        
        The logic:
          1) Build the "validity map" from viewer's perspective.
          2) If target is invalid => return not trusted.
          3) If target is implicit => self-trust.
          4) If target is complete => show "complete trust path" if any.
          5) If target is marginal => show "partial paths" (since presumably
             user got marginal from partial signers).
        """
        # Quick checks for existence
        if viewer not in self.users or target not in self.users:
            return {
                "trusted": False,
                "trust_level": TrustLevel.INVALID.value,
                "reason": "One or both users don't exist",
                "paths": []
            }

        # 1) Build the final validity map
        validity_map = self.compute_validity_map(viewer)

        # 2) Check what the final trust level is for target
        final_level = validity_map[target]

        if final_level == TrustLevel.IMPLICIT:
            return {
                "trusted": True,
                "trust_level": TrustLevel.IMPLICIT.value,
                "reason": "Self trust (implicit)",
                "paths": [[viewer]]  # trivial path
            }
        elif final_level == TrustLevel.COMPLETE:
            # Show all complete-edge paths (since that caused completeness)
            paths = self.find_complete_paths(viewer, target, validity_map)
            return {
                "trusted": True,
                "trust_level": TrustLevel.COMPLETE.value,
                "reason": "User is fully trusted",
                "paths": paths
            }
        elif final_level == TrustLevel.MARGINAL:
            # Show partial-edge paths. There may be more than one.
            paths = self.find_partial_paths(viewer, target, validity_map)
            return {
                "trusted": True,
                "trust_level": TrustLevel.MARGINAL.value,
                "reason": "User is marginally trusted (2 or more partial signers)",
                "paths": paths
            }
        else:
            # INVALID
            return {
                "trusted": False,
                "trust_level": TrustLevel.INVALID.value,
                "reason": "Not trusted by viewer",
                "paths": []
            }
