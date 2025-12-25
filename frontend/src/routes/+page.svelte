<script lang="ts">
	import { session, hasSession } from '$lib/stores/session';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import ChatInterface from '$lib/components/ChatInterface.svelte';
</script>

<svelte:head>
	<title>Movie Order Form Filler</title>
	<meta name="description" content="AI-powered movie order form assistant" />
</svelte:head>

<div class="app">
	<aside class="sidebar">
		<div class="logo">
			<svg viewBox="0 0 24 24" fill="currentColor">
				<path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
			</svg>
			<span>Form Filler</span>
		</div>
		<nav>
			<a href="/" class="nav-item active">
				<svg viewBox="0 0 24 24" fill="currentColor">
					<path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-9 13H9v-2h2v2zm0-4H9V9h2v2zm0-4H9V5h2v2zm4 8h-2v-2h2v2zm0-4h-2V9h2v2zm0-4h-2V5h2v2zm4 8h-2v-2h2v2zm0-4h-2V9h2v2zm0-4h-2V5h2v2z"/>
				</svg>
				Order Form
			</a>
		</nav>
		<div class="sidebar-footer">
			<p>Powered by Google ADK</p>
		</div>
	</aside>

	<main>
		<div class="content">
			{#if $hasSession}
				<ChatInterface />
			{:else}
				<div class="welcome">
					<h1>Movie Order Form Filler</h1>
					<p class="subtitle">Upload your order form and let AI help you fill it out</p>
					<FileUpload />
					<div class="features">
						<div class="feature">
							<svg viewBox="0 0 24 24" fill="currentColor">
								<path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
							</svg>
							<span>Validates shipping countries</span>
						</div>
						<div class="feature">
							<svg viewBox="0 0 24 24" fill="currentColor">
								<path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
							</svg>
							<span>Adds multiple movies</span>
						</div>
						<div class="feature">
							<svg viewBox="0 0 24 24" fill="currentColor">
								<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
							</svg>
							<span>Preserves document formatting</span>
						</div>
					</div>
				</div>
			{/if}
		</div>
	</main>
</div>

<style>
	:global(:root) {
		--bg: #0f0f14;
		--surface: #16161e;
		--surface-elevated: #1e1e2e;
		--surface-hover: #252535;
		--border-color: #2a2a3a;
		--text-primary: #f1f1f5;
		--text-secondary: #a1a1aa;
		--accent: #7c3aed;
		--accent-hover: #6d28d9;
		--error: #ef4444;
	}

	:global(*) {
		box-sizing: border-box;
	}

	:global(body) {
		margin: 0;
		font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		background: var(--bg);
		color: var(--text-primary);
		-webkit-font-smoothing: antialiased;
	}

	.app {
		display: flex;
		min-height: 100vh;
	}

	.sidebar {
		width: 260px;
		background: var(--surface);
		border-right: 1px solid var(--border-color);
		display: flex;
		flex-direction: column;
		padding: 1.5rem;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding-bottom: 1.5rem;
		border-bottom: 1px solid var(--border-color);
		margin-bottom: 1.5rem;
	}

	.logo svg {
		width: 32px;
		height: 32px;
		color: var(--accent);
	}

	.logo span {
		font-size: 1.25rem;
		font-weight: 700;
		letter-spacing: -0.02em;
	}

	nav {
		flex: 1;
	}

	.nav-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		border-radius: 10px;
		color: var(--text-secondary);
		text-decoration: none;
		font-weight: 500;
		transition: all 0.15s ease;
	}

	.nav-item:hover {
		background: var(--surface-hover);
		color: var(--text-primary);
	}

	.nav-item.active {
		background: var(--accent);
		color: white;
	}

	.nav-item svg {
		width: 20px;
		height: 20px;
	}

	.sidebar-footer {
		padding-top: 1rem;
		border-top: 1px solid var(--border-color);
	}

	.sidebar-footer p {
		margin: 0;
		font-size: 0.75rem;
		color: var(--text-secondary);
	}

	main {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.content {
		flex: 1;
		padding: 2rem;
		max-width: 900px;
		margin: 0 auto;
		width: 100%;
	}

	.welcome {
		max-width: 600px;
		margin: 0 auto;
		padding-top: 4rem;
	}

	.welcome h1 {
		margin: 0 0 0.5rem;
		font-size: 2.5rem;
		font-weight: 700;
		letter-spacing: -0.03em;
		text-align: center;
		background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent) 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.subtitle {
		margin: 0 0 2.5rem;
		text-align: center;
		color: var(--text-secondary);
		font-size: 1.125rem;
	}

	.features {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-top: 2.5rem;
		padding: 1.5rem;
		background: var(--surface);
		border-radius: 12px;
		border: 1px solid var(--border-color);
	}

	.feature {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: var(--text-secondary);
		font-size: 0.95rem;
	}

	.feature svg {
		width: 20px;
		height: 20px;
		color: #22c55e;
	}
</style>
