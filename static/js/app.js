/**
 * APP.JS - FANCY VERSION
 * Connected to Flask Backend + Handles Stats & Badges
 */

const API = {
    // 1. Get All Chemicals
    getAllChemicals: async () => {
        const response = await fetch('/api/chemicals');
        return await response.json();
    },

    // 2. Get Single Chemical
    getChemicalById: async (id) => {
        const response = await fetch(`/api/chemicals/${id}`);
        return await response.json();
    },

    // 3. Get Locations
    getLocations: async () => {
        const response = await fetch('/api/locations');
        return await response.json();
    },

    // 4. Save (Add or Update)
    saveChemical: async (data) => {
        const response = await fetch('/api/chemicals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Failed to save');
        }
        return await response.json();
    },

    // 5. Delete
    deleteChemical: async (id) => {
        await fetch(`/api/chemicals/${id}`, { method: 'DELETE' });
    },

    // 6. PubChem Suggest
    suggestChemical: async (name) => {
        const response = await fetch('/api/chemicals/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Suggestion failed');
        }
        return await response.json();
    }
};



/**
 * UI CONTROLLER
 */
const InventoryApp = {
    locationsCache: [], // Cache for modal

    // --- DASHBOARD LOGIC ---
    initDashboard: async () => {
        const tableBody = document.getElementById('inventoryTableBody');
        const searchInput = document.getElementById('searchInput');
        const locFilter = document.getElementById('locationFilter');

        // 1. Fetch Real Data (Parallel for speed)
        const [chemicals, locations] = await Promise.all([
            API.getAllChemicals(),
            API.getLocations()
        ]);

        // Save to cache & build fast lookup map
        InventoryApp.locationsCache = locations;
        const locMap = {};
        locations.forEach(l => locMap[l.id] = l.name);

        // 2. Update Stats Cards & Notifications
        const lowStock = chemicals.filter(c => c.quantity < 50);
        const today = new Date();
        const expiring = chemicals.filter(c => {
            if (!c.expiry_date) return false;
            const expDate = new Date(c.expiry_date);
            const diffTime = expDate - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            return diffDays <= 30;
        });

        // Update Stats
        if (document.getElementById('statTotal')) {
            document.getElementById('statTotal').innerText = chemicals.length;
            document.getElementById('statLow').innerText = lowStock.length;
            document.getElementById('statLocs').innerText = locations.length;
        }

        // Update Notifications
        const notifBadge = document.getElementById('notificationCount');
        const notifList = document.getElementById('notificationList');
        const totalAlerts = lowStock.length + expiring.length;

        if (totalAlerts > 0 && notifBadge && notifList) {
            notifBadge.innerText = totalAlerts;
            notifBadge.style.display = 'block';

            let html = '';

            // Low Stock Alerts
            lowStock.forEach(c => {
                html += `
                    <div class="p-3 border-bottom d-flex align-items-start bg-warning bg-opacity-10">
                        <i class="fa-solid fa-triangle-exclamation text-warning mt-1 me-3"></i>
                        <div>
                            <p class="mb-0 fw-bold text-dark">Low Stock: ${c.name}</p>
                            <small class="text-muted">Only ${c.quantity} ${c.unit} remaining.</small>
                        </div>
                    </div>
                `;
            });

            // Expiry Alerts
            expiring.forEach(c => {
                const isExpired = new Date(c.expiry_date) < today;
                const txt = isExpired ? 'Expired' : 'Expiring Soon';
                const color = isExpired ? 'danger' : 'info';
                html += `
                    <div class="p-3 border-bottom d-flex align-items-start bg-${color} bg-opacity-10">
                        <i class="fa-solid fa-clock text-${color} mt-1 me-3"></i>
                        <div>
                            <p class="mb-0 fw-bold text-dark">${txt}: ${c.name}</p>
                            <small class="text-muted">Date: ${c.expiry_date.split('T')[0]}</small>
                        </div>
                    </div>
                `;
            });
            notifList.innerHTML = html;
        } else if (notifList) {
            notifList.innerHTML = `
                <div class="p-4 text-center text-muted small">
                    <i class="fa-solid fa-check-circle mb-2 text-success fa-2x"></i>
                    <p class="mb-0">All good! No alerts.</p>
                </div>
            `;
            if (notifBadge) notifBadge.style.display = 'none';
        }

        // 3. Populate Filter Dropdown
        locFilter.innerHTML = '<option value="">All Locations</option>';
        locations.forEach(loc => {
            const opt = document.createElement('option');
            opt.value = loc.id;
            opt.textContent = loc.name;
            locFilter.appendChild(opt);
        });

        // 4. Render "Fancy" Table
        const renderTable = (data) => {
            tableBody.innerHTML = '';
            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No chemicals found in database.</td></tr>';
                return;
            }

            data.forEach(chem => {
                // Fast O(1) Lookup using locMap
                const locName = chem.location_name || locMap[chem.location_id] || 'Unknown';
                const expiry = chem.expiry_date ? chem.expiry_date.toString().split('T')[0] : 'N/A';

                // Status Badge Logic
                let statusBadge = '<span class="badge bg-success bg-opacity-10 text-success">In Stock</span>';
                if (chem.quantity < 50) {
                    statusBadge = '<span class="badge bg-warning bg-opacity-10 text-warning">Low Stock</span>';
                }

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="ps-4 fw-bold text-dark"><a href="#" class="text-decoration-none text-dark" onclick="InventoryApp.showDetails(${chem.id}); return false;">${chem.name}</a></td>
                    <td class="text-muted">${chem.cas_number}</td>
                    <td>${statusBadge}</td>
                    <td><small class="text-secondary fw-semibold">${locName}</small></td>
                    <td>${expiry}</td>
                    <td class="text-end pe-4">
                        <button class="btn btn-sm btn-light text-info me-1" onclick="InventoryApp.editChem(${chem.id})"><i class="fa-solid fa-pen"></i></button>
                        <button class="btn btn-sm btn-light text-danger" onclick="InventoryApp.deleteChem(${chem.id})"><i class="fa-regular fa-trash-can"></i></button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        };

        // Filter Logic
        const filterData = () => {
            const term = searchInput.value.toLowerCase();
            const locId = locFilter.value;
            const filtered = chemicals.filter(c => {
                const matchesName = c.name.toLowerCase().includes(term) || c.cas_number.includes(term);
                const matchesLoc = locId ? c.location_id == locId : true;
                return matchesName && matchesLoc;
            });
            renderTable(filtered);
        };

        searchInput.addEventListener('keyup', filterData);
        locFilter.addEventListener('change', filterData);
        renderTable(chemicals);
    },

    // --- UI HELPERS ---
    showDetails: async (id) => {
        try {
            const chem = await API.getChemicalById(id);
            if (!chem || chem.error) throw new Error("Chemical not found");

            // Populate Modal Fields
            document.getElementById('modalName').textContent = chem.name;
            document.getElementById('modalCAS').textContent = chem.cas_number || 'N/A';
            document.getElementById('modalQty').textContent = `${chem.quantity} ${chem.unit}`;

            // Location Name (Backend includes location_name in get_chemical join? Let's check. 
            // Actually get_chemical endpoint just does SELECT * FROM chemicals. 
            // We might need to fetch locations or just show ID if name isn't there.
            // Wait, renderTable had access to location list. 
            // A better way: Let's fetch locations if needed or rely on what we have. 
            // The API.getChemicalById returns just the chemical row. 
            // Let's do a quick fetch of locations to map the name, or just show "Location ID: ...". 
            // Ideally backend should return it. 
            // Use Cache for Location Name
            let locName = 'Unknown Location';
            if (chem.location_name) {
                locName = chem.location_name;
            } else {
                // Check cache, if empty fetch again (fallback)
                if (InventoryApp.locationsCache.length === 0) {
                    InventoryApp.locationsCache = await API.getLocations();
                }
                const foundLoc = InventoryApp.locationsCache.find(l => l.id == chem.location_id);
                if (foundLoc) locName = foundLoc.name;
            }
            document.getElementById('modalLoc').textContent = locName;

            document.getElementById('modalExpiry').textContent = chem.expiry_date ? chem.expiry_date.split('T')[0] : 'No Expiry Date';
            document.getElementById('modalSafety').textContent = chem.safety_notes || 'No specific safety notes recorded.';

            // Badge
            const badgeDiv = document.getElementById('modalStatusBadge');
            if (chem.quantity < 50) {
                badgeDiv.innerHTML = '<span class="badge bg-warning text-dark px-3 py-2 rounded-pill"><i class="fa-solid fa-triangle-exclamation me-2"></i>Low Stock</span>';
            } else {
                badgeDiv.innerHTML = '<span class="badge bg-success text-white px-3 py-2 rounded-pill"><i class="fa-solid fa-check me-2"></i>In Stock</span>';
            }

            // Bind Actions in Manage Tab
            const editBtn = document.getElementById('modalEditBtn');
            const delBtn = document.getElementById('modalDeleteBtn');

            // Clone to remove previous listeners
            const newEditBtn = editBtn.cloneNode(true);
            const newDelBtn = delBtn.cloneNode(true);
            editBtn.parentNode.replaceChild(newEditBtn, editBtn);
            delBtn.parentNode.replaceChild(newDelBtn, delBtn);

            newEditBtn.onclick = () => InventoryApp.editChem(chem.id);
            newDelBtn.onclick = () => InventoryApp.deleteChem(chem.id);

            // Show Modal
            const modalEl = document.getElementById('quickViewModal');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();

        } catch (e) {
            console.error(e);
            alert("Failed to load details.");
        }
    },

    editChem: (id) => {
        window.location.href = `form.html?id=${id}`;
    },

    deleteChem: async (id) => {
        if (confirm('Are you sure you want to permanently delete this chemical?')) {
            await API.deleteChemical(id);
            window.location.reload();
        }
    },

    // --- FORM LOGIC (Unchanged) ---
    initForm: async () => {
        const locSelect = document.getElementById('location_id');
        const locations = await API.getLocations();

        locations.forEach(loc => {
            const opt = document.createElement('option');
            opt.value = loc.id;
            opt.textContent = loc.name;
            locSelect.appendChild(opt);
        });

        const urlParams = new URLSearchParams(window.location.search);
        const editId = urlParams.get('id');

        if (editId) {
            document.getElementById('pageTitle').textContent = "Edit Chemical";
            const chem = await API.getChemicalById(editId);
            if (chem && !chem.error) {
                document.getElementById('chemId').value = chem.id;
                document.getElementById('name').value = chem.name;
                document.getElementById('cas_number').value = chem.cas_number;
                document.getElementById('quantity').value = chem.quantity;
                document.getElementById('unit').value = chem.unit;
                document.getElementById('location_id').value = chem.location_id;
                if (chem.expiry_date) {
                    document.getElementById('expiry_date').value = chem.expiry_date.split('T')[0];
                }
                document.getElementById('safety_notes').value = chem.safety_notes || '';
            }
        }

        document.getElementById('chemicalForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                id: document.getElementById('chemId').value || null,
                name: document.getElementById('name').value,
                cas_number: document.getElementById('cas_number').value,
                quantity: parseFloat(document.getElementById('quantity').value),
                unit: document.getElementById('unit').value,
                location_id: document.getElementById('location_id').value || null,
                expiry_date: document.getElementById('expiry_date').value,
                safety_notes: document.getElementById('safety_notes').value
            };
            try {
                await API.saveChemical(formData);
                alert('Saved!');
                window.location.href = '/chemicals';
            } catch (err) { alert(err.message); }
        });
    },

    // --- AI SUGGESTION UI LOGIC ---
    suggestChemicalInfo: async () => {
        const nameInput = document.getElementById('name');
        const spinner = document.getElementById('suggestSpinner');
        const btn = document.getElementById('btnSuggest');

        const chemicalName = nameInput.value.trim();
        if (!chemicalName) {
            alert('Please enter a chemical name first.');
            return;
        }

        // UI Feedback
        spinner.classList.remove('d-none');
        btn.disabled = true;

        try {
            const data = await API.suggestChemical(chemicalName);

            if (data) {
                // Populate Fields
                if (data.name) document.getElementById('name').value = data.name;
                if (data.cas_number) document.getElementById('cas_number').value = data.cas_number;
                if (data.safety_notes) document.getElementById('safety_notes').value = data.safety_notes;

                // Suggest location if it matches existing locations
                if (data.suggested_location) {
                    const locSelect = document.getElementById('location_id');
                    const locOptions = Array.from(locSelect.options);
                    const match = locOptions.find(opt =>
                        opt.text.toLowerCase().includes(data.suggested_location.toLowerCase()) ||
                        data.suggested_location.toLowerCase().includes(opt.text.toLowerCase())
                    );
                    if (match) locSelect.value = match.value;
                }

                console.log("Suggestion applied:", data);
            }
        } catch (err) {
            console.error(err);
            alert('Error getting suggestion: ' + err.message);
        } finally {
            spinner.classList.add('d-none');
            btn.disabled = false;
        }
    }
};

