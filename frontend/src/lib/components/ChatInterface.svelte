<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { session, canDownload } from '$lib/stores/session';
	import { sendMessage, createEventSource, getDownloadUrl } from '$lib/api';
	import MessageBubble from './MessageBubble.svelte';

	let inputValue = $state('');
	let isSending = $state(false);
	let messagesContainer: HTMLElement;
	let eventSource: EventSource | null = null;

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	function connectSSE() {
		const sessionId = $session.sessionId;
		if (!sessionId) return;

		eventSource = createEventSource(sessionId);
		session.setConnected(true);

		eventSource.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);

				if (data.type === 'message' && data.content) {
					session.addMessage('assistant', data.content);
					scrollToBottom();
				} else if (data.type === 'done') {
					if (data.is_complete) {
						session.setComplete(true);
					}
					// Reconnect for next interaction
					reconnectSSE();
				} else if (data.type === 'error') {
					session.setError(data.content);
				}
			} catch {
				// Ignore parse errors (keepalives, etc.)
			}
		};

		eventSource.onerror = () => {
			session.setConnected(false);
			// Try to reconnect after a delay
			setTimeout(reconnectSSE, 2000);
		};
	}

	function reconnectSSE() {
		if (eventSource) {
			eventSource.close();
		}
		if ($session.sessionId) {
			connectSSE();
		}
	}

	async function handleSubmit() {
		const message = inputValue.trim();
		if (!message || isSending || !$session.sessionId) return;

		inputValue = '';
		isSending = true;

		session.addMessage('user', message);
		scrollToBottom();

		try {
			await sendMessage($session.sessionId, message);
		} catch (error) {
			session.setError(error instanceof Error ? error.message : 'Failed to send message');
		} finally {
			isSending = false;
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit();
		}
	}

	function handleDownload() {
		if ($session.sessionId) {
			window.open(getDownloadUrl($session.sessionId), '_blank');
		}
	}

	function handleNewSession() {
		if (eventSource) {
			eventSource.close();
		}
		session.reset();
	}

	onMount(() => {
		if ($session.sessionId) {
			connectSSE();
		}
	});

	onDestroy(() => {
		if (eventSource) {
			eventSource.close();
		}
	});

	$effect(() => {
		if ($session.sessionId && !eventSource) {
			connectSSE();
		}
	});
</script>

<div class="chat-container">
	<header class="chat-header">
		<div class="header-content">
			<h2>Movie Order Form</h2>
			<span class="status" class:connected={$session.isConnected}>
				{$session.isConnected ? 'Connected' : 'Connecting...'}
			</span>
		</div>
		<div class="header-actions">
			{#if $canDownload}
				<button class="download-btn" onclick={handleDownload}>
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
						<polyline points="7 10 12 15 17 10" />
						<line x1="12" y1="15" x2="12" y2="3" />
					</svg>
					Download Filled Form
				</button>
			{/if}
			<button class="new-btn" onclick={handleNewSession}>New Form</button>
		</div>
	</header>

	<div class="messages" bind:this={messagesContainer}>
		{#each $session.messages as message (message.id)}
			<MessageBubble {message} />
		{/each}

		{#if $session.messages.length === 0}
			<div class="empty-state">
				<p>Connecting to the assistant...</p>
			</div>
		{/if}
	</div>

	<form class="input-area" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
		<textarea
			bind:value={inputValue}
			onkeydown={handleKeydown}
			placeholder="Type your message..."
			rows="1"
			disabled={isSending}
		></textarea>
		<button type="submit" disabled={!inputValue.trim() || isSending} aria-label="Send message">
			<svg viewBox="0 0 24 24" fill="currentColor">
				<path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
			</svg>
		</button>
	</form>

	{#if $session.error}
		<div class="error-toast">
			<p>{$session.error}</p>
			<button onclick={() => session.setError(null)}>×</button>
		</div>
	{/if}
</div>

<style>
	.chat-container {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--surface, #16161e);
		border-radius: 16px;
		overflow: hidden;
		border: 1px solid var(--border-color, #2a2a3a);
	}

	.chat-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.5rem;
		background: var(--surface-elevated, #1e1e2e);
		border-bottom: 1px solid var(--border-color, #2a2a3a);
	}

	.header-content h2 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--text-primary, #f1f1f5);
	}

	.status {
		font-size: 0.75rem;
		color: var(--text-secondary, #a1a1aa);
		display: flex;
		align-items: center;
		gap: 0.375rem;
	}

	.status::before {
		content: '';
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--text-secondary, #a1a1aa);
	}

	.status.connected::before {
		background: #22c55e;
	}

	.header-actions {
		display: flex;
		gap: 0.75rem;
	}

	.download-btn,
	.new-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.download-btn {
		background: var(--accent, #7c3aed);
		color: white;
	}

	.download-btn:hover {
		background: var(--accent-hover, #6d28d9);
	}

	.download-btn svg {
		width: 16px;
		height: 16px;
	}

	.new-btn {
		background: var(--surface, #16161e);
		color: var(--text-secondary, #a1a1aa);
		border: 1px solid var(--border-color, #2a2a3a);
	}

	.new-btn:hover {
		background: var(--surface-hover, #252535);
		color: var(--text-primary, #f1f1f5);
	}

	.messages {
		flex: 1;
		overflow-y: auto;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: var(--text-secondary, #a1a1aa);
	}

	.input-area {
		display: flex;
		gap: 0.75rem;
		padding: 1rem 1.5rem;
		background: var(--surface-elevated, #1e1e2e);
		border-top: 1px solid var(--border-color, #2a2a3a);
	}

	.input-area textarea {
		flex: 1;
		padding: 0.75rem 1rem;
		border: 1px solid var(--border-color, #2a2a3a);
		border-radius: 12px;
		background: var(--surface, #16161e);
		color: var(--text-primary, #f1f1f5);
		font-family: inherit;
		font-size: 0.95rem;
		resize: none;
		outline: none;
		transition: border-color 0.15s ease;
	}

	.input-area textarea:focus {
		border-color: var(--accent, #7c3aed);
	}

	.input-area textarea::placeholder {
		color: var(--text-secondary, #a1a1aa);
	}

	.input-area button {
		width: 48px;
		height: 48px;
		border: none;
		border-radius: 12px;
		background: var(--accent, #7c3aed);
		color: white;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.15s ease;
	}

	.input-area button:hover:not(:disabled) {
		background: var(--accent-hover, #6d28d9);
	}

	.input-area button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.input-area button svg {
		width: 20px;
		height: 20px;
	}

	.error-toast {
		position: absolute;
		bottom: 100px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.75rem 1rem;
		background: var(--error, #ef4444);
		color: white;
		border-radius: 8px;
		animation: slideUp 0.2s ease-out;
	}

	.error-toast p {
		margin: 0;
	}

	.error-toast button {
		background: none;
		border: none;
		color: white;
		font-size: 1.25rem;
		cursor: pointer;
		opacity: 0.8;
	}

	.error-toast button:hover {
		opacity: 1;
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateX(-50%) translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateX(-50%) translateY(0);
		}
	}
</style>

