<!-- For anyone connecting this, I think the implementation of websocket is pretty straight forward, please 
 make sure to use to only be sending a JSON to the front end so it works right out of the box. -->

 <!-- for the stats, I will work on that as soon as I am getting real data to understand what I have to do. -->
<script>
    import { onMount } from 'svelte';
    let results = [];
    let socket;
    onMount(() => {
      socket = new WebSocket("ws://localhost:8000/ws/scan");  // !!!! here change for the link of the web socket!!!!!!!!
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        results = [...results, ...data]; // to append
      };
      socket.onerror = (e) => {
        console.error("WebSocket error:", e);
      };
      socket.onclose = () => {
        console.log("WebSocket closed");
      };
    });

    let targetUrl = '';
	let attackType = '';
	let header = '';
	let payloads = '';
	let injectionPoints = '';
	let hideStatusCodes = '';
	let showOnlyStatusCodes = '';
	let proxy = '';
	let additionalParams = '';

	function startAttack() {
		console.log('Starting attack with: ', {
			targetUrl,
			attackType,
			header,
			payloads,
			injectionPoints,
			hideStatusCodes,
			showOnlyStatusCodes,
			proxy,
			additionalParams
		});

		// Your attack logic here
	}
  // Variables for control
  let paused = false;
  let progress = 0;
  let running = false;
  let interval;
  
  

  function startProgress() {
  progress = 0;
  running = true;
  paused = false;

  clearInterval(interval); 
  interval = setInterval(() => {
    if (!paused && progress < 100) {
      progress += 1;
    } else if (progress >= 100) {
      running = false;
      clearInterval(interval);
    }
  }, 100);
}


function restartProgress() {
  progress = 0;
  running = false;
  paused = false;

  clearInterval(interval); // por si estaba corriendo

  setTimeout(() => {
    console.log('Restarting process');
    startProgress();
  }, 2500); // 2.5 segundos
}



  onMount(() => {
		const params = new URLSearchParams(window.location.search);

		targetUrl = params.get('targetUrl') ?? '';
		attackType = params.get('attackType') ?? '';
		header = params.get('header') ?? '';
		payloads = params.get('payloads') ?? '';
		injectionPoints = params.get('injectionPoints') ?? '';
		hideStatusCodes = params.get('hideStatusCodes') ?? '';
		showOnlyStatusCodes = params.get('showOnlyStatusCodes') ?? '';
		proxy = params.get('proxy') ?? '';
		additionalParams = params.get('additionalParams') ?? '';

		startAttack(); // automatically trigger it on page load
	});
  onMount(() => {
  startProgress();
});



</script>



<div class="flex min-h-screen">
  <div class="flex-1 flex flex-col ml-20"> 
  <main class="flex-1 overflow-auto px-8 pt-8 pb-4">
 
    
    <div class="mb-8">
      <p class="text-sm mb-1 font-medium">{Math.floor(progress)}%</p>
      <div class="w-full h-2 bg-gray-200 rounded-full">
        <div
          class="h-2 bg-cyan-500 rounded-lg transition-all duration-500"
          style="width: {progress}%"
        ></div>
      </div>
      <p class="text-xs mt-1 text-cyan-600">{running ? 'Scanning...' : 'Idle'}</p>
    </div>
    
    <div class="stats-row">
      <div>
        <p class="text-gray-500">Running Time</p>
        <p class="font-bold text-xl">{(progress * 3).toFixed(1)}</p> 
      </div>
      <div>
        <p class="text-gray-500">Processed Requests</p>
        <!-- <p class="font-bold text-xl">{Math.floor(progress * 10)}</p> -->
      </div>
      <div>
        <p class="text-gray-500">Filtered Requests</p>
        <!-- <p class="font-bold text-xl">{Math.floor(progress * 2)}</p> -->
      </div>
      <div>
        <p class="text-gray-500">Requests/sec.</p>
        <!-- <p class="font-bold text-xl">{(Math.random() * 0.5 + 0.2).toFixed(3)}</p> -->
      </div>
    </div>
    
     <div class="overflow-x-auto rounded-2xl shadow-md mb-8">
        <table class="  min-w-full text-sm text-left bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)]">
          <thead class="bg-[var(--accent3)]  text-[var(--accent3-foreground)] uppercase text-xs font-semibold">
           <!-- <thead> -->
            <tr>
              <th class="header-table">Request</th>
              <th class="header-table">Position</th>
              <th class="header-table">Payload</th>
              <th class="header-table">Status</th>
              <th class="header-table">Error</th>
              <th class="header-table">Timeout</th>
              <th class="header-table">Length</th>
            </tr>
          </thead>
          <tbody>
            {#each results as row, i}
              <tr class="odd:bg-[var(--card)] even:bg-[var(--background1)] border-b border-[var(--border)]">
                <td class="px-4 py-3 tracking-widest">{row.request}</td>
                <td class="px-4 py-3">{row.position}</td>
                <td class="px-4 py-3">{row.payloads}</td>
                <td class="px-4 py-3">{row.status}</td>
                <td class="px-4 py-3">{row.error}</td>
                <td class="px-4 py-3">{row.timeout}</td>
                <td class="px-4 py-3">{row.length}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
   
  </main>

  </div>
 
  <footer class="fixed bottom-0 left-20 right-0 py-4 px-8 z-10 bg-transparent">
    <div class="flex justify-end gap-4">
      <button on:click={() => paused = !paused} class="bg-[var(--accent3)] text-black font-semibold px-6 py-3 rounded-lg hover:opacity-90">
        {paused ? 'Resume' : 'Pause'}
      </button>
      <button on:click={restartProgress} class="bg-[var(--accent3)] text-black font-semibold px-6 py-3 rounded-lg hover:opacity-90">
        Restart
      </button>
      <button class="bg-[var(--accent3)] text-black font-semibold px-6 py-3 rounded-lg hover:opacity-90">
        Modify
      </button>
    </div>
  </footer>
  
</div>



  
  

<style>
/* table {
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 0.3rem;
} */
th, td {
  padding: 0.75rem;
  text-align: left;
}
/* .header-table{
  background: #9BC2CB;
} */

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  text-align: center;
  margin-bottom: 2rem;
}

</style>