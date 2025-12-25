<script lang="ts">
	import { session } from '$lib/stores/session';
	import { uploadDocument } from '$lib/api';

	let isDragging = $state(false);
	let fileInput: HTMLInputElement;

	async function handleFile(file: File) {
		if (!file.name.endsWith('.docx')) {
			session.setError('Please upload a .docx file');
			return;
		}

		session.setUploading(true);
		session.setError(null);

		try {
			const response = await uploadDocument(file);
			session.setSession(response.session_id);
		} catch (error) {
			session.setError(error instanceof Error ? error.message : 'Upload failed');
		} finally {
			session.setUploading(false);
		}
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		isDragging = false;

		const file = event.dataTransfer?.files[0];
		if (file) {
			handleFile(file);
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		isDragging = true;
	}

	function handleDragLeave() {
		isDragging = false;
	}

	function handleInputChange(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (file) {
			handleFile(file);
		}
	}

	function triggerFileInput() {
		fileInput.click();
	}
</script>

<div
	class="upload-zone"
	class:dragging={isDragging}
	class:uploading={$session.isUploading}
	ondrop={handleDrop}
	ondragover={handleDragOver}
	ondragleave={handleDragLeave}
	onclick={triggerFileInput}
	onkeydown={(e) => e.key === 'Enter' && triggerFileInput()}
	role="button"
	tabindex="0"
>
	<input
		bind:this={fileInput}
		type="file"
		accept=".docx"
		onchange={handleInputChange}
		hidden
	/>

	{#if $session.isUploading}
		<div class="loader"></div>
		<p>Uploading document...</p>
	{:else}
		<svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
			<polyline points="17 8 12 3 7 8" />
			<line x1="12" y1="3" x2="12" y2="15" />
		</svg>
		<h3>Upload Order Form</h3>
		<p>Drag & drop your .docx file here, or click to browse</p>
	{/if}

	{#if $session.error}
		<p class="error">{$session.error}</p>
	{/if}
</div>

<style>
	.upload-zone {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		padding: 4rem 2rem;
		border: 2px dashed var(--border-color, #3a3a4a);
		border-radius: 16px;
		background: var(--surface-elevated, #1e1e2e);
		cursor: pointer;
		transition: all 0.2s ease;
		min-height: 280px;
	}

	.upload-zone:hover,
	.upload-zone.dragging {
		border-color: var(--accent, #7c3aed);
		background: var(--surface-hover, #252535);
	}

	.upload-zone.uploading {
		pointer-events: none;
		opacity: 0.8;
	}

	.upload-icon {
		width: 64px;
		height: 64px;
		color: var(--accent, #7c3aed);
	}

	h3 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--text-primary, #f1f1f5);
	}

	p {
		margin: 0;
		color: var(--text-secondary, #a1a1aa);
		font-size: 0.95rem;
	}

	.error {
		color: var(--error, #ef4444);
		font-weight: 500;
	}

	.loader {
		width: 48px;
		height: 48px;
		border: 4px solid var(--border-color, #3a3a4a);
		border-top-color: var(--accent, #7c3aed);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>


