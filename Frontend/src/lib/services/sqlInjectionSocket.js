import { serviceStatus } from '$lib/stores/projectServiceStore';
import { scanProgress, stopScanProgress, startScanProgress, scanPaused} from '$lib/stores/scanProgressStore';
import { serviceResults } from '$lib/stores/serviceResultsStore.js';
import { get } from 'svelte/store';
import { getApiBaseURL } from '$lib/utils/apiBaseURL';

let socket = null;

/**
 * Establishes a WebSocket connection to the backend SQLInjection service using the job ID.
 * Automatically retries connection if it fails (up to maxRetries).
 */
export function connectToSQLInjectionWebSocket(jobId, retry = 0) {
  const maxRetries = 5;

  // Prevent duplicate connections if one is already open
  if (socket && socket.readyState !== WebSocket.CLOSED) {
    console.warn('[WebSocket] Already connected. Skipping duplicate connection.');
    return;
  }

  // apiBaseURL is fetched from a utility function
  const apiBaseURL = getApiBaseURL();
  const wsBaseURL = apiBaseURL.replace('http', 'ws');

  // Open a WebSocket connection to the backend endpoint
  socket = new WebSocket(`${wsBaseURL}/ws/sqlinjection/${jobId}`);

  // Triggered when the connection is successfully established
  socket.onopen = () => {
    console.log('[WebSocket] Connected to SQLInjection job:', jobId);
  };

  // Triggered whenever a message is received from the backend
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    const { type, data } = message;

    switch (type) {
      // Updates job status in the serviceStatus store
      case 'status': {
        const mappedStatus = data.status;
        const current = get(serviceStatus);
      
        // Ignore downgrades from completed → idle
        if (current.status === 'completed' && mappedStatus === 'idle') {
          console.warn('[SQLInjection] Ignoring idle status after completion');
          return;
        }
      
        // handle pause/resume toggling
        switch (mappedStatus) {
          case 'paused':
            scanPaused.set(true);
            break;
          case 'running':
            scanPaused.set(false);
            break;
        }
      
        serviceStatus.set({
          status: mappedStatus,
          serviceType: 'sqlinjection',
          startTime: data.started_at || new Date().toISOString()
        });
        break;
      }
      
      // Updates the sqlinjection result table with a new scanned row
      case 'new_row':
        serviceResults.update((r) => ({
          ...r,
          sqlinjection: [...r.sqlinjection, data.row]
        }));
        break;

      // Updates the progress of the sqlinjection job
      case 'progress':
        if (get(serviceStatus).status === 'completed') {
          console.warn('[SQLInjection] Ignoring late progress update');
          return;
        }
        if (!get(scanPaused)) {
          startScanProgress('sqlinjection');
          scanProgress.set(Math.min(data.progress, 99));
        }
        break;

      // Marks the scan as completed and finalizes UI
      case 'completed':
        scanProgress.set(100);
        stopScanProgress(true);
        serviceStatus.set({
          status: 'completed',
          serviceType: 'sqlinjection',
          startTime: null
        });
        break;

      // Handles errors and resets UI state
      case 'error':
        serviceStatus.set({
          status: 'idle',
          serviceType: 'sqlinjection',
          startTime: null
        });
        console.error('[SQLInjection Error]', data.message);
        break;

      // Logs backend messages to console for debugging
      case 'log':
        console.log(`[SQLInjection Log] ${data.message}`);
        break;
    }
  };

  // Handles WebSocket connection errors and retries if needed
  socket.onerror = (e) => {
    console.error('[WebSocket Error]', e);

    if (retry < maxRetries) {
      console.log(`[WebSocket] Retrying connection (${retry + 1}/${maxRetries})...`);
      setTimeout(() => connectToSQLInjectionWebSocket(jobId, retry + 1), 1000);
    }
  };

  // Cleans up socket reference when connection is closed
  socket.onclose = () => {
    console.log('[WebSocket] Connection closed');
    socket = null;
  };
}

/**
 * Manually closes the WebSocket connection.
 */
export function closeSQLInjectionWebSocket() {
  const status = get(serviceStatus).status;

  if (status === 'paused' || status === 'running') {
    console.log('[WebSocket] Not closing — scan still active or paused.');
    return;
  }

  if (socket) {
    socket.close();
    socket = null;
    console.log('[WebSocket] Closed manually.');
  }
}