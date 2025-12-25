const API_BASE = 'http://localhost:8000/api';

export interface UploadResponse {
	session_id: string;
	message: string;
}

export interface StatusResponse {
	is_complete: boolean;
	form_data: {
		name: string | null;
		street: string | null;
		postal_code_city: string | null;
		country: string | null;
		movies: Array<{ title: string; language: string }>;
	};
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${API_BASE}/upload`, {
		method: 'POST',
		body: formData
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Upload failed');
	}

	return response.json();
}

export async function sendMessage(sessionId: string, message: string): Promise<void> {
	const response = await fetch(`${API_BASE}/chat/${sessionId}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ message })
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to send message');
	}
}

export function createEventSource(sessionId: string): EventSource {
	return new EventSource(`${API_BASE}/chat/stream/${sessionId}`);
}

export async function getStatus(sessionId: string): Promise<StatusResponse> {
	const response = await fetch(`${API_BASE}/status/${sessionId}`);

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to get status');
	}

	return response.json();
}

export function getDownloadUrl(sessionId: string): string {
	return `${API_BASE}/download/${sessionId}`;
}


