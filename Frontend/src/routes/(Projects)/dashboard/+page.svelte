<script>
	import { onMount, tick } from 'svelte';
	import CreateProjectModal from '$lib/components/ui/project_management/CreateProjectModal.svelte';
	import ImportProjectModal from '$lib/components/ui/project_management/ImportProjectModal.svelte';
	import EditProjectDialog from '$lib/components/ui/project_management/EditProjectDialog.svelte';
	import {
		DropdownMenu,
		DropdownMenuTrigger,
		DropdownMenuContent,
		DropdownMenuItem
	} from '$lib/components/ui/dropdown-menu';
	import { CalendarIcon, Lock, Settings2, MoreHorizontal, Trash2 } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	import {
		AlertDialog,
		AlertDialogTrigger,
		AlertDialogContent,
		AlertDialogHeader,
		AlertDialogFooter,
		AlertDialogTitle,
		AlertDialogDescription,
		AlertDialogCancel,
		AlertDialogAction
	} from '$lib/components/ui/alert-dialog';

	import Alert from '$lib/components/ui/alert/Alert.svelte';

	let projects = [];
	let isLoading = true;
	let error = null;
	let analystInitials = '';
	let analystId = '';
	let showCreateModal = false;
	let showImportModal = false;

	let editDialogOpen = false;
	let currentProject = null;

	let projectToDelete = null;
	let showDeleteDialog = false; //come back

	let apiBaseURL = '';

	onMount(async () => {
		analystInitials = localStorage.getItem('analyst_initials') || '';
		analystId = localStorage.getItem('analyst_id') || '';

		if (!analystInitials || !analystId) {
			window.location.href = '/login';
			return;
		}

		await loadProjects();
	});

	async function loadProjects() {
	isLoading = true;
	error = null;
		try {
			const response = await fetch(`http://127.0.0.1:8000/team3/projects/analyst/${analystId}`);
			if (!response.ok) throw new Error('Failed to load projects');
			const data = await response.json();
			projects = data.projects || [];
		} catch (err) {
			console.error('Error loading projects:', err);
			error = err.message;
			projects = [];
		} finally {
			isLoading = false;
		}
	}

	// Commented out, used for testing getting job ids. 
	//  Make API Call to leads backend
	// async function fetchProjectSpecificData() {
	// 	if (!apiBaseURL) {
	// 		console.error('API Base URL not set!');
	// 		return;
	// 	}

	// 	const response = await fetch(`${apiBaseURL}/graphql`, {
	// 		method: 'POST',
	// 		headers: { 'Content-Type': 'application/json' },
	// 		body: JSON.stringify({
	// 			query: `query { getCrawlerJobStatus(jobId: "4d72c256-73f5-4076-9f3a-799d29897b00") }`
	// 		})
	// 	});

	// 	const data = await response.json();
	// 	console.log('Project-specific data:', data);
	// }

	function openCreateModal() {
		showCreateModal = true;
	}

	function closeCreateModal() {
		showCreateModal = false;
	}

	async function handleProjectCreated(event) {
		try {
			const projectData = event.detail;

			console.log(projectData);

			const response = await fetch('http://127.0.0.1:8000/team3/projects/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					analyst_id: analystId,
					project_name: projectData.projectName,
					start_date: projectData.startDate,
					end_date: projectData.endDate,
					description: projectData.description || '',
					userList: projectData.userList || []
				})
			});

			const responseData = await response.json();
			if (!response.ok) {
				let errorMessage = 'Failed to create project';
				if (responseData.detail) {
					// If it's a string or something printable
					errorMessage =
						typeof responseData.detail === 'string'
							? responseData.detail
							: JSON.stringify(responseData.detail);
				} else if (typeof responseData === 'object') {
					errorMessage = JSON.stringify(responseData);
				}

				throw new Error(errorMessage);
			}

			await loadProjects();
			closeCreateModal();
		} catch (err) {
			if (err instanceof Error) {
				console.error('Error creating project:', err.message);
				error = err.message;
			} else {
				console.error('Unknown error creating project:', JSON.stringify(err, null, 2));
				error = 'An unknown error occurred';
			}
		}
	}

	function handleImportProject(event) {
		const { files } = event.detail;
		console.log('Importing project files:', files);
		showImportModal = false;
	}

	function handleLogout() {
		localStorage.removeItem('analyst_id');
		localStorage.removeItem('analyst_initials');
		window.location.href = '/login';
	}

	async function toggleProjectLock(projectName) {
		console.log('Toggling lock for:', projectName, 'by', analystInitials);
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/team3/projects/${encodeURIComponent(projectName)}/lock?analyst_id=${analystInitials}`,
				{
					method: 'PUT'
				}
			);

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.detail || 'Failed to update lock status');
			}

			await loadProjects(); // Refresh projects list
		} catch (err) {
			console.error('Error toggling lock:', err);
			error = err.message;
		}
	}

	window.toggleProjectLock = toggleProjectLock;

	async function deleteProject(name) {
		console.log('Deleting project:', name); // Not working
		try {
			showDeleteDialog = false;
			const response = await fetch(
				`http://127.0.0.1:8000/team3/projects/${encodeURIComponent(name)}/delete?analyst_id=${analystId}`,
				{
					method: 'DELETE'
				}
			);

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.detail || 'Failed to delete project');
			}

			await loadProjects(); // Reload after deletion
			console.log(`Project '${name}' deleted successfully`);
		} catch (err) {
			console.error('Error deleting project:', err);
			error = err.message;
		}
	}

	function confirmDelete(project) {
		console.log('message from confirm delete: Project', project.name); // 👈 This is working
		projectToDelete = project;
		showDeleteDialog = true;
	}

	async function handleConfirmedDelete() {
		console.log('message from handle confirmed delete: Project', projectToDelete.name); // Not working
		if (projectToDelete) {
			await deleteProject(projectToDelete.name);
			showDeleteDialog = false;
			projectToDelete = null;
		}
	}

	function handleCancelDelete() {
		showDeleteDialog = false; // Close the dialog when canceled
	}

	async function openEditDialog(project) {
		currentProject = project;
		editDialogOpen = false; // Force it closed first
		await tick(); // Wait for DOM update cycle
		editDialogOpen = true; // Now reopen
		console.log(currentProject);
	}

	function handleSave(updatedProject) {
		// Save logic here, such as updating the project in your state or database
		console.log('Save event received in parent:', updatedProject);
		editDialogOpen = false; // Close the dialog after saving
	}
	function handleCancel() {
		editDialogOpen = false; // Close the dialog when canceled
	}

	let openDropdownId = null;

	function toggleDropdown(id) {
		openDropdownId = openDropdownId === id ? null : id;
	}

	function closeDropdown() {
		openDropdownId = null;
	}

	function handleClickOutside(event) {
		if (!event.target.closest('.options-wrapper')) {
			closeDropdown();
		}
	}

	onMount(() => {
		window.addEventListener('click', handleClickOutside);
	});
</script>

<div class="p-6">
	<header class="mb-8 flex items-center justify-between">
		<h1 class="text-3xl font-bold">Project Selection</h1>
		<div class="flex items-center gap-4">
			<span class="text-muted-foreground text-sm">Analyst: {analystInitials}</span>
			<button
				class="rounded-md bg-red-500 px-3 py-1 text-sm font-medium text-white hover:bg-red-600"
				on:click={handleLogout}
			>
				Logout
			</button>
		</div>
	</header>

	<div class="mb-6 flex items-center justify-between">
		<h2 class="text-2xl font-semibold">Your Projects</h2>
		<button
			class="bg-primary hover:bg-primary/90 rounded-md px-4 py-2 text-sm font-medium text-white shadow"
			on:click={openCreateModal}
		>
			Create New Project
		</button>
	</div>

	{#if isLoading}
		<div class="text-gray-500">Loading projects...</div>
	{:else if error}
		<div class="text-red-500">Error: {error}</div>
	{:else if projects.length === 0}
		<div class="mt-12 space-y-4 text-center">
			<p class="text-lg">You don't have any projects yet.</p>
			<button
				class="bg-primary hover:bg-primary/90 rounded-md px-4 py-2 text-white shadow"
				on:click={openCreateModal}
			>
				Create Your First Project
			</button>
		</div>
	{:else}
		<div class="space-y-4">
			<!-- Column Headers -->
			<div class="text-muted-foreground grid grid-cols-4 px-6 py-2 text-sm font-semibold">
				<div>Project Name</div>
				<div>Last Edit</div>
				<div>Lead Analyst</div>
				<div class="pr-4 text-right"></div>
				<!-- delete maybe-->
			</div>

			{#each projects as project (project.id)}
				<div
					class="bg-card border-border grid grid-cols-4 items-center rounded-2xl border px-6 py-4 shadow-sm"
				>
					<!-- Project Info -->
					<div class="flex items-center gap-4">
						<!-- Colored status bar -->
						<div
							class="h-12 w-1.5 rounded-full"
							class:bg-green-500={!project.locked}
							class:bg-red-500={project.locked}
						></div>
						<div>
							<h3 class="text-foreground text-base font-semibold">{project?.name}</h3>
						</div>
					</div>

					<!-- Last Edit -->
					<div class="text-muted-foreground text-sm">{project.timestamp || 'N/A'}</div>

					<!-- Lead Analyst -->
					<div class="text-muted-foreground text-sm">{analystInitials}</div>

					<!-- Lock icon + button -->
					<div class="flex items-center justify-end gap-3">
						{#if project.locked}
							<Lock class="text-muted-foreground h-5 w-5" />
						{/if}

						{#if project}
							<button
								class="rounded-md bg-[var(--secondary)] px-4 py-2 text-sm font-medium text-[var(--secondary-foreground)] hover:bg-[color:var(--secondary)/90]"
								on:click={async () => {
									if (!project.locked) {
										apiBaseURL = `http://${project.lead_ip}:8000`;
										localStorage.setItem('apiBaseURL', apiBaseURL);  // Save to local storage
										console.log('API BASE URL set to:', apiBaseURL);
									}
								}}
							>
								{project.locked ? 'View' : 'Run Scan'}
							</button>
						{/if}

						<!-- Drop Down: Lock, Delete, and Edit -->
						<div class="options-wrapper relative">
							<button
								class="options-btn hover:bg-muted rounded p-1"
								on:click|stopPropagation={() => toggleDropdown(project.id)}
							>
								<MoreHorizontal class="h-5 w-5" />
							</button>
							{#if openDropdownId === project.id}
								<div
									class="absolute right-0 z-50 mt-2 w-32 rounded-md border border-gray-200 bg-white shadow-md dark:border-gray-700 dark:bg-gray-800"
								>
									<button
										class="text-muted-foreground flex w-full items-center gap-2 px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
										on:click={() => toggleProjectLock(project.name)}
									>
										<Lock class="h-4 w-4" />
										{project.locked ? 'Unlock' : 'Lock'}
									</button>

									{#if !project.locked}
										<!-- Use !project.locked to check when it's unlocked -->
										<!-- Add Edit Button -->
										<button
											class="text-muted-foreground flex w-full items-center gap-2 px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
											on:click={() => {
												openEditDialog(project);
												closeDropdown();
											}}
										>
											<Settings2 class="h-4 w-4" />
											Edit
										</button>
										<button
											class="text-muted-foreground flex w-full items-center gap-2 px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
											on:click={() => confirmDelete(project)}
										>
											<Trash2 class="h-4 w-4" />
											Delete
										</button>
									{/if}
								</div>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	{#if showCreateModal}
		<CreateProjectModal {analystId} on:close={closeCreateModal} on:create={handleProjectCreated} />
	{/if}

	{#if showImportModal}
		<ImportProjectModal
			on:close={() => (showImportModal = false)}
			on:import={handleImportProject}
		/>
	{/if}

	{#if editDialogOpen}
		<EditProjectDialog project={currentProject} on:save={handleSave} on:cancel={handleCancel} />
	{/if}

	<Alert
		isOpen={showDeleteDialog}
		title="Are you absolutely sure?"
		message="This action cannot be undone."
		onCancel={handleCancelDelete}
		onContinue={handleConfirmedDelete}
	/>
</div>
