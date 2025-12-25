<script lang="ts">
	import type { Message } from '$lib/stores/session';

	interface Props {
		message: Message;
	}

	let { message }: Props = $props();
</script>

<div class="message" class:user={message.role === 'user'} class:assistant={message.role === 'assistant'}>
	<div class="avatar">
		{#if message.role === 'user'}
			<svg viewBox="0 0 24 24" fill="currentColor">
				<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
			</svg>
		{:else}
			<svg viewBox="0 0 24 24" fill="currentColor">
				<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
			</svg>
		{/if}
	</div>
	<div class="content">
		<p>{message.content}</p>
		<time>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time>
	</div>
</div>

<style>
	.message {
		display: flex;
		gap: 0.75rem;
		max-width: 85%;
		animation: fadeIn 0.2s ease-out;
	}

	.message.user {
		flex-direction: row-reverse;
		margin-left: auto;
	}

	.message.assistant {
		margin-right: auto;
	}

	.avatar {
		flex-shrink: 0;
		width: 36px;
		height: 36px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.message.user .avatar {
		background: var(--accent, #7c3aed);
		color: white;
	}

	.message.assistant .avatar {
		background: var(--surface-elevated, #2a2a3a);
		color: var(--accent, #7c3aed);
	}

	.avatar svg {
		width: 20px;
		height: 20px;
	}

	.content {
		padding: 0.875rem 1rem;
		border-radius: 16px;
	}

	.message.user .content {
		background: var(--accent, #7c3aed);
		color: white;
		border-bottom-right-radius: 4px;
	}

	.message.assistant .content {
		background: var(--surface-elevated, #2a2a3a);
		color: var(--text-primary, #f1f1f5);
		border-bottom-left-radius: 4px;
	}

	.content p {
		margin: 0;
		line-height: 1.5;
		white-space: pre-wrap;
	}

	.content time {
		display: block;
		margin-top: 0.375rem;
		font-size: 0.75rem;
		opacity: 0.7;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>


