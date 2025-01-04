<template>
  <v-stage :config="{ width: 500, height: 400 }">
    <v-layer>
      <v-circle :config="{ x: 250, y: 200, radius: 50, fill: 'blue' }" />
    </v-layer>
  </v-stage>
</template>

<script>
import { Stage, Rect, Text } from 'vue-konva'
export default {
  name: 'App',
  components: {
    'v-stage': Stage,
    'v-layer': Layer,
    'v-circle': Circle,
  }
}
</script>
