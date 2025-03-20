<script lang="ts">
  let temp = 0;
  function getTemp(){
    fetch(`https://${location.host}:8443/temp`)
    .then((response) => response.text())
    .then((text) => {
      temp = (text/1000).toFixed(1);
    });
  }
  setInterval(getTemp, 2000);
</script>

<div>{temp}C</div>
