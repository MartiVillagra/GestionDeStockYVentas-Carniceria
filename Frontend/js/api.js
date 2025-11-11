// js/api.js

const BASE_URL = "http://127.0.0.1:8000"; // Cambia si usás otro puerto o despliegue

// Función genérica para llamar a la API
async function apiCall(endpoint, method = "GET", data = null) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (data) options.body = JSON.stringify(data);

  const response = await fetch(`${BASE_URL}/${endpoint}`, options);
  if (!response.ok) throw new Error("Error en la solicitud: " + response.status);
  return await response.json();
}
