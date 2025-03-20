<script lang="ts">
  function turnLedOn(){
    fetch('./ledon')
  }
  function turnLedOff(){
    fetch('./ledoff')
  }
</script>
Turn led: 
<button on:click={turnLedOn}>On</button>
<button on:click={turnLedOff}>Off</button>