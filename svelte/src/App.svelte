<script lang="ts">
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
  import Video from './lib/Video.svelte'
  import LedToggle from './lib/LedToggle.svelte'
  import Temp from './lib/Temp.svelte'

</script>

<main>
  <div>
    <LedToggle/>
  </div>
  <div>
    <Temp/>
  </div>
  <div>
    <Video />
  </div>

  <p class="read-the-docs">
    Simple camera thingy.
  </p>
</main>

<style>
  div {
    margin-bottom:10px;
  }
  .read-the-docs {
    color: #888;
  }
</style>
