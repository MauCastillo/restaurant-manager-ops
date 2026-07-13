document.addEventListener("DOMContentLoaded", () => {
    // 1. Auto-dismiss Toast notifications after 5 seconds
    const toasts = document.querySelectorAll(".alert-toast");
    toasts.forEach((toast) => {
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(20px)";
            toast.style.transition = "all 0.4s ease";
            setTimeout(() => toast.remove(), 400);
        }, 5000);
    });

    // 2. Modal Controls
    const openModalButtons = document.querySelectorAll("[data-modal-target]");
    const closeModalButtons = document.querySelectorAll("[data-close-modal]");
    const overlays = document.querySelectorAll(".modal-overlay");

    openModalButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-modal-target");
            const modal = document.getElementById(targetId);
            if (modal) {
                modal.classList.add("active");
            }
        });
    });

    closeModalButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".modal-overlay");
            if (modal) {
                modal.classList.remove("active");
            }
        });
    });

    overlays.forEach((overlay) => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) {
                overlay.classList.remove("active");
            }
        });
    });

    // 3. Client table real-time filter helper
    const searchInput = document.getElementById("tableSearchInput");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const term = e.target.value.toLowerCase().trim();
            const rows = document.querySelectorAll(".filterable-table tbody tr");
            rows.forEach((row) => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? "" : "none";
            });
        });
    }

    // 4. Interactive Client Autocomplete Searcher for Sales/Purchases
    const autocompleteWrappers = document.querySelectorAll("[data-client-autocomplete]");
    autocompleteWrappers.forEach((wrapper) => {
        const input = wrapper.querySelector(".autocomplete-input");
        const dropdown = wrapper.querySelector(".autocomplete-dropdown");
        const hiddenIdInput = wrapper.querySelector("input[name='client_id']");
        const selectedBadge = wrapper.querySelector(".selected-client-display");
        let debounceTimer = null;
        let activeIndex = -1;
        let currentResults = [];

        if (!input || !dropdown) return;

        function closeDropdown() {
            dropdown.classList.remove("active");
            dropdown.innerHTML = "";
            activeIndex = -1;
        }

        function renderResults(results) {
            currentResults = results;
            dropdown.innerHTML = "";
            if (results.length === 0) {
                dropdown.innerHTML = `<div style="padding: 0.75rem 1rem; color: var(--text-muted); font-size: 0.85rem;">No se encontraron clientes coincidentes</div>`;
                dropdown.classList.add("active");
                return;
            }

            results.forEach((client, idx) => {
                const item = document.createElement("div");
                item.className = "autocomplete-item";
                item.setAttribute("data-idx", idx);
                item.innerHTML = `
                    <span class="autocomplete-item-title">${client.nombre}</span>
                    <span class="autocomplete-item-sub">CC: ${client.cedula}</span>
                `;

                item.addEventListener("click", () => selectClient(client));
                dropdown.appendChild(item);
            });
            dropdown.classList.add("active");
        }

        function selectClient(client) {
            hiddenIdInput.value = client.id;
            input.value = client.nombre;
            closeDropdown();

            if (selectedBadge) {
                selectedBadge.style.display = "flex";
                selectedBadge.innerHTML = `
                    <span>✓ Seleccionado: <strong>${client.nombre}</strong> (Cédula: ${client.cedula})</span>
                    <span style="cursor:pointer; opacity:0.8;" onclick="this.parentElement.style.display='none'; document.querySelector('input[name=\\'client_id\\']').value='';">Cambiar</span>
                `;
            }

            const form = wrapper.closest("form");
            if (form && form.hasAttribute("data-auto-submit")) {
                form.submit();
            }
        }

        input.addEventListener("input", (e) => {
            const query = e.target.value.trim();
            if (hiddenIdInput) hiddenIdInput.value = "";
            if (selectedBadge) selectedBadge.style.display = "none";

            clearTimeout(debounceTimer);
            if (query.length < 1) {
                closeDropdown();
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/clients/api/search?q=${encodeURIComponent(query)}`);
                    if (res.ok) {
                        const data = await res.json();
                        renderResults(data);
                    }
                } catch (err) {
                    console.error("Error buscando clientes:", err);
                }
            }, 180);
        });

        input.addEventListener("keydown", (e) => {
            const items = dropdown.querySelectorAll(".autocomplete-item");
            if (!dropdown.classList.contains("active") || items.length === 0) return;

            if (e.key === "ArrowDown") {
                e.preventDefault();
                activeIndex = (activeIndex + 1) % items.length;
                updateFocusedItem(items);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                activeIndex = (activeIndex - 1 + items.length) % items.length;
                updateFocusedItem(items);
            } else if (e.key === "Enter" && activeIndex >= 0 && currentResults[activeIndex]) {
                e.preventDefault();
                selectClient(currentResults[activeIndex]);
            } else if (e.key === "Escape") {
                closeDropdown();
            }
        });

        function updateFocusedItem(items) {
            items.forEach((item, idx) => {
                item.classList.toggle("focused", idx === activeIndex);
            });
        }

        document.addEventListener("click", (e) => {
            if (!wrapper.contains(e.target)) {
                closeDropdown();
            }
        });
    });

    // 5. Persistent Date Selector & One-Click Calendar Picker
    const allDateInputs = document.querySelectorAll("input[type='date']");
    allDateInputs.forEach((dateInput) => {
        dateInput.addEventListener("click", () => {
            try {
                if (typeof dateInput.showPicker === "function") {
                    dateInput.showPicker();
                }
            } catch (err) {
                // Ignore if browser restricts showPicker invocation
            }
        });
    });

    const persistentDateInputs = document.querySelectorAll(".persistent-date-input");
    const lastDate = localStorage.getItem("last_fecha_compra");
    const todayStr = new Date().toISOString().split("T")[0];

    persistentDateInputs.forEach((dateInput) => {
        dateInput.value = lastDate || todayStr;
        dateInput.addEventListener("change", (e) => {
            if (e.target.value) {
                localStorage.setItem("last_fecha_compra", e.target.value);
            }
        });
    });

    // 6. Check if we should reopen the createPurchaseModal for consecutive entries
    const shouldReopen = localStorage.getItem("reopen_purchase_modal");
    if (shouldReopen === "1") {
        const modal = document.getElementById("createPurchaseModal");
        if (modal) {
            modal.classList.add("active");
            const searchInput = modal.querySelector(".autocomplete-input");
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        }
    }

    // 7. Duplicate Purchase Detection & Form Submission Handler
    const purchaseForms = document.querySelectorAll("[data-purchase-form]");
    purchaseForms.forEach((form) => {
        const forceDupInput = form.querySelector("input[name='force_duplicate']");
        const dupBanner = form.querySelector(".duplicate-alert-banner");
        const dupMsg = form.querySelector(".duplicate-msg");
        const cancelBtn = form.querySelector(".cancel-dup-btn");
        const confirmBtn = form.querySelector(".confirm-dup-btn");
        const keepOpenCheckbox = form.querySelector(".keep-open-checkbox");

        if (cancelBtn) {
            cancelBtn.addEventListener("click", () => {
                if (dupBanner) dupBanner.style.display = "none";
            });
        }

        if (confirmBtn) {
            confirmBtn.addEventListener("click", () => {
                if (forceDupInput) forceDupInput.value = "1";
                handleKeepOpenPreference();
                form.submit();
            });
        }

        function handleKeepOpenPreference() {
            if (keepOpenCheckbox && keepOpenCheckbox.checked) {
                localStorage.setItem("reopen_purchase_modal", "1");
            } else {
                localStorage.removeItem("reopen_purchase_modal");
            }
        }

        form.addEventListener("submit", async (e) => {
            if (forceDupInput && forceDupInput.value === "1") {
                handleKeepOpenPreference();
                return; // Let regular submit proceed
            }

            e.preventDefault();

            const clientId = form.querySelector("input[name='client_id']").value;
            const fechaCompra = form.querySelector("input[name='fecha_compra']").value;
            const monto = form.querySelector("input[name='monto']").value;

            // Persist the date on submit
            if (fechaCompra) {
                localStorage.setItem("last_fecha_compra", fechaCompra);
            }

            try {
                const res = await fetch(`/purchases/api/check_duplicate?client_id=${encodeURIComponent(clientId)}&fecha_compra=${encodeURIComponent(fechaCompra)}&monto=${encodeURIComponent(monto)}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.is_duplicate) {
                        if (dupMsg) {
                            dupMsg.textContent = `Atención: El cliente ya tiene un registro guardado en la fecha ${fechaCompra} por el mismo valor ($${parseFloat(monto).toFixed(2)}). Puede ser un registro duplicado por error. ¿Deseas guardarlo de todos modos?`;
                        }
                        if (dupBanner) dupBanner.style.display = "block";
                        return;
                    }
                }
            } catch (err) {
                console.error("Error consultando duplicado:", err);
            }

            // Not duplicate or error checking -> submit normally
            handleKeepOpenPreference();
            form.submit();
        });
    });

    // 8. Dark / Light Theme Switcher
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const themeIcon = document.getElementById("themeToggleIcon");
    const themeLabel = document.getElementById("themeToggleLabel");

    function updateThemeUI() {
        const isLight = document.documentElement.getAttribute("data-theme") === "light";
        if (themeIcon && themeLabel) {
            themeIcon.textContent = isLight ? "🌙" : "☀️";
            themeLabel.textContent = isLight ? "Oscuro" : "Claro";
        }
    }

    updateThemeUI();

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const isLight = document.documentElement.getAttribute("data-theme") === "light";
            if (isLight) {
                document.documentElement.removeAttribute("data-theme");
                localStorage.setItem("hexops_theme", "dark");
            } else {
                document.documentElement.setAttribute("data-theme", "light");
                localStorage.setItem("hexops_theme", "light");
            }
            updateThemeUI();
        });
    }
});
