import { writable, derived } from 'svelte/store';

export interface Message {
	id: string;
	role: 'user' | 'assistant';
	content: string;
	timestamp: Date;
}

export interface SessionState {
	sessionId: string | null;
	isUploading: boolean;
	isComplete: boolean;
	messages: Message[];
	isConnected: boolean;
	error: string | null;
}

function createSessionStore() {
	const { subscribe, set, update } = writable<SessionState>({
		sessionId: null,
		isUploading: false,
		isComplete: false,
		messages: [],
		isConnected: false,
		error: null
	});

	return {
		subscribe,
		setSession: (sessionId: string) =>
			update((state) => ({ ...state, sessionId, error: null })),
		setUploading: (isUploading: boolean) =>
			update((state) => ({ ...state, isUploading })),
		setComplete: (isComplete: boolean) =>
			update((state) => ({ ...state, isComplete })),
		setConnected: (isConnected: boolean) =>
			update((state) => ({ ...state, isConnected })),
		setError: (error: string | null) =>
			update((state) => ({ ...state, error })),
		addMessage: (role: 'user' | 'assistant', content: string) =>
			update((state) => ({
				...state,
				messages: [
					...state.messages,
					{
						id: crypto.randomUUID(),
						role,
						content,
						timestamp: new Date()
					}
				]
			})),
		reset: () =>
			set({
				sessionId: null,
				isUploading: false,
				isComplete: false,
				messages: [],
				isConnected: false,
				error: null
			})
	};
}

export const session = createSessionStore();

export const hasSession = derived(session, ($session) => $session.sessionId !== null);
export const canDownload = derived(session, ($session) => $session.isComplete);


