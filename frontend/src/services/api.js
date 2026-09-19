const API_BASE_URL = "http://localhost:5000/api";


export async function checkBackend() {

    const response = await fetch(
        `${API_BASE_URL}/health`
    );

    if (!response.ok) {
        throw new Error("Backend request failed");
    }

    return await response.json();
}


export async function analyzeTask(taskData) {

    const response = await fetch(
        `${API_BASE_URL}/analyze-task`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(taskData)
        }
    );

    if (!response.ok) {
        throw new Error("Task analysis request failed");
    }

    return await response.json();
}


export async function generateSchedule(projectData) {

    const response = await fetch(
        `${API_BASE_URL}/schedule`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(projectData)
        }
    );

    if (!response.ok) {
        throw new Error("Scheduling request failed");
    }

    return await response.json();
}


export async function recalculateSchedule(projectData) {

    const response = await fetch(
        `${API_BASE_URL}/recalculate`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(projectData)
        }
    );

    if (!response.ok) {
        throw new Error("Recalculation request failed");
    }

    return await response.json();
}