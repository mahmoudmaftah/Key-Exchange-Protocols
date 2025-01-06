from enum import Enum
from collections import defaultdict
from typing import Dict, Set, List, Optional

class TrustLevel(Enum):
    IMPLICIT = "implicit"
    COMPLETE = "complete"
    PARTIAL = "partial"
    MARGINAL = "marginal"
    INVALID = "invalid"

class PGPTrustWeb:
    def __init__(self):
        self.users: Set[str] = set()
        self.direct_trust: Dict[str, Dict[str, str]] = defaultdict(dict)
        
    def add_node(self, name: str) -> bool:
        if name in self.users:
            return False
        self.users.add(name)
        self.direct_trust[name][name] = TrustLevel.IMPLICIT.value
        return True

    def add_signature(self, signer: str, target: str, trust_level: str) -> dict:
        if signer not in self.users or target not in self.users:
            return {"success": False, "message": "One or both users don't exist"}
        
        if signer == target:
            return {"success": False, "message": "Cannot explicitly sign own key"}

        self.direct_trust[signer][target] = trust_level
        return {"success": True}

    def _find_all_paths(self, start: str, end: str, visited: Set[str], path: List[str]) -> List[List[str]]:
        """Find all possible paths between start and end nodes"""
        paths = []
        visited.add(start)
        path.append(start)

        if start == end and len(path) > 1:
            paths.append(path[:])
        else:
            for next_user in self.direct_trust[start]:
                if next_user not in visited:
                    new_paths = self._find_all_paths(next_user, end, visited.copy(), path[:])
                    paths.extend(new_paths)

        return paths

    def is_partial_path(self, path: List[str]) -> bool:
        """Check if a path consists of all partial trust relationships"""
        for i in range(len(path) - 1):
            trust_level = self.direct_trust[path[i]][path[i + 1]]
            if trust_level != TrustLevel.PARTIAL.value:
                return False
        return True

    def is_complete_path(self, path: List[str]) -> bool:
        """Check if a path consists of all complete trust relationships"""
        for i in range(len(path) - 1):
            trust_level = self.direct_trust[path[i]][path[i + 1]]
            if trust_level != TrustLevel.COMPLETE.value:
                return False
        return True

    def find_partial_paths(self, viewer: str, target: str) -> List[List[str]]:
        """Find all paths that consist of partial trust relationships"""
        all_paths = self._find_all_paths(viewer, target, set(), [])
        return [path for path in all_paths if all(
            self.direct_trust[path[i]][path[i+1]] == TrustLevel.PARTIAL.value 
            for i in range(len(path)-1)
        )]

    def find_complete_paths(self, viewer: str, target: str) -> List[List[str]]:
        """Find all paths that consist of complete trust relationships"""
        all_paths = self._find_all_paths(viewer, target, set(), [])
        return [path for path in all_paths if all(
            self.direct_trust[path[i]][path[i+1]] == TrustLevel.COMPLETE.value 
            for i in range(len(path)-1)
        )]

    def check_trust(self, viewer: str, target: str) -> dict:
        """Determine trust level between viewer and target"""
        if viewer not in self.users or target not in self.users:
            return {
                "trusted": False,
                "trust_level": TrustLevel.INVALID.value,
                "reason": "One or both users don't exist",
                "paths": []
            }

        # Case 1: Implicit self-trust
        if viewer == target:
            return {
                "trusted": True,
                "trust_level": TrustLevel.IMPLICIT.value,
                "reason": "Self trust (implicit)",
                "paths": [[viewer]]
            }

        # Find all paths first
        complete_paths = self.find_complete_paths(viewer, target)
        partial_paths = self.find_partial_paths(viewer, target)

        # Case 2: Complete trust path exists
        if complete_paths:
            return {
                "trusted": True,
                "trust_level": TrustLevel.COMPLETE.value,
                "reason": "Complete trust path exists",
                "paths": complete_paths
            }

        # Case 3: Multiple partial paths
        if len(partial_paths) >= 2:
            return {
                "trusted": True,
                "trust_level": TrustLevel.MARGINAL.value,
                "reason": f"Marginal trust through {len(partial_paths)} partial trust paths",
                "paths": partial_paths
            }

        # Case 4: Single partial path
        if len(partial_paths) == 1:
            return {
                "trusted": False,
                "trust_level": TrustLevel.INVALID.value,
                "reason": "Only one partial trust path (insufficient)",
                "paths": partial_paths
            }

        # Case 5: No valid paths
        return {
            "trusted": False,
            "trust_level": TrustLevel.INVALID.value,
            "reason": "No valid trust paths found",
            "paths": []
        }