const API_URL = "http://localhost:8000";

// Charger les données au démarrage
document.addEventListener('DOMContentLoaded', loadData);

function getCollection() {
    return document.getElementById('collectionName').value || "current_weather_clean";
}

function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    setTimeout(() => alertContainer.innerHTML = '', 4000);
}

async function loadData() {
    const collection = getCollection();
    try {
        const response = await fetch(`${API_URL}/weather_data?collection_name=${collection}`);
        if (!response.ok) throw new Error("Erreur réseau");
        const data = await response.json();
        renderTable(data);
    } catch (error) {
        console.error(error);
        showAlert("Impossible de charger les données. Vérifiez que l'API tourne sur le port 8000.", "danger");
    }
}

function renderTable(data) {
    const tbody = document.getElementById('dataTableBody');
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center">Aucune donnée trouvée dans cette collection.</td></tr>';
        return;
    }

    data.forEach(item => {
        const id = item._id;
        const displayItem = { ...item };
        delete displayItem._id; // On masque l'ID dans le JSON pour éviter la redondance

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><small class="text-muted">${id}</small></td>
            <td><pre class="m-0">${JSON.stringify(displayItem, null, 2)}</pre></td>
            <td>
                <button class="btn btn-sm btn-warning action-btn" onclick='editItem(${JSON.stringify(item)})'>Éditer</button>
                <button class="btn btn-sm btn-danger action-btn" onclick="deleteItem('${id}')">Suppr.</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function saveData() {
    const id = document.getElementById('editId').value;
    const jsonText = document.getElementById('jsonData').value;
    const collection = getCollection();
    
    let payload;
    try {
        payload = JSON.parse(jsonText);
    } catch (e) {
        alert("Le format JSON est invalide ! Vérifiez les guillemets et la syntaxe.");
        return;
    }
    delete payload._id; // Sécurité : on ne laisse pas l'utilisateur modifier l'ID manuellement dans le corps

    try {
        let url = `${API_URL}/weather_data`;
        let method = 'POST';

        if (id) {
            url += `/${id}`;
            method = 'PUT';
        }

        // Ajout du paramètre collection_name
        url += `?collection_name=${collection}`;

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Erreur API");
        
        showAlert(id ? "Mise à jour réussie" : "Ajout réussi");
        resetForm();
        loadData();
    } catch (error) {
        console.error(error);
        showAlert("Erreur lors de l'enregistrement", "danger");
    }
}

async function deleteItem(id) {
    if (!confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) return;
    
    const collection = getCollection();
    try {
        const response = await fetch(`${API_URL}/weather_data/${id}?collection_name=${collection}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error("Erreur suppression");
        showAlert("Élément supprimé");
        loadData();
    } catch (error) {
        console.error(error);
        showAlert("Erreur lors de la suppression", "danger");
    }
}

function editItem(item) {
    document.getElementById('editId').value = item._id;
    const displayItem = { ...item };
    delete displayItem._id;
    
    document.getElementById('jsonData').value = JSON.stringify(displayItem, null, 4);
    
    // Changement visuel du formulaire
    const header = document.getElementById('formHeader');
    header.innerText = "Modifier l'entrée " + item._id;
    header.classList.replace('bg-success', 'bg-warning');
    header.classList.add('text-dark');
    header.classList.remove('text-white');
    
    const btn = document.getElementById('btnSave');
    btn.innerText = "Mettre à jour";
    btn.classList.replace('btn-success', 'btn-warning');
    
    window.scrollTo(0, 0);
}

function resetForm() {
    document.getElementById('editId').value = '';
    document.getElementById('jsonData').value = '';
    
    // Reset visuel
    const header = document.getElementById('formHeader');
    header.innerText = "Ajouter une nouvelle entrée";
    header.classList.replace('bg-warning', 'bg-success');
    header.classList.remove('text-dark');
    header.classList.add('text-white');

    const btn = document.getElementById('btnSave');
    btn.innerText = "Ajouter";
    btn.classList.replace('btn-warning', 'btn-success');
}