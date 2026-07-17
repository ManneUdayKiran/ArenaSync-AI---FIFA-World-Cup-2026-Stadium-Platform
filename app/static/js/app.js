// State Management
let appState = {
    currentRole: 'fan', // fan, volunteer, organizer
    currentTab: 'chat-tab',
    language: 'en',
    ttsEnabled: false,
    fontSize: 16,
    activeIncidentId: null,
    chatHistory: {
        fan: [{ role: 'model', content: 'Welcome! I am your AI Stadium Assistant. How can I guide you through the World Cup match operations today?' }],
        volunteer: [{ role: 'model', content: 'Volunteer Coordinator AI active. Welcome to your shift! Let\'s ensure a secure and smooth tournament experience. Let me know if you need instructions on crowd control, accessibility escorts, or reporting an incident.' }],
        organizer: [{ role: 'model', content: 'Operations Intelligence Copilot active. Monitoring gate congestions, incident queues, and utility status. How can I assist you with resource reallocation or public safety announcements?' }]
    }
};

// DOM Elements
const docBody = document.body;
const srAnnounce = document.getElementById('sr-announcements');
const tabPanels = document.querySelectorAll('.tab-panel');
const navItems = document.querySelectorAll('.nav-item');
const roleButtons = document.querySelectorAll('.role-btn');

// Start up Initializations
document.addEventListener('DOMContentLoaded', () => {
    initAppRouting();
    initRoleSwitcher();
    initAccessibilityControls();
    initChatInterface();
    initMapTrafficInterface();
    initSustainabilityInterface();
    initCommandCenterInterface();
    
    // Load initial data
    refreshGatesTraffic();
    refreshLeaderboard();
    refreshIncidentsFeed();
    loadSuggestedQueries();
    
    announceA11y("ArenaSync AI FIFA 2026 loaded. Fan mode active.");
});

// A11y Announcements helper
function announceA11y(message) {
    if (srAnnounce) {
        srAnnounce.textContent = message;
    }
}

// 1. Navigation Panel Routing
function initAppRouting() {
    navItems.forEach(button => {
        button.addEventListener('click', () => {
            const targetedTab = button.getAttribute('data-tab');
            
            // Update nav item state
            navItems.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            });
            button.classList.add('active');
            button.setAttribute('aria-selected', 'true');
            
            // Switch panel display
            tabPanels.forEach(panel => panel.classList.remove('active'));
            const activePanel = document.getElementById(targetedTab);
            activePanel.classList.add('active');
            
            appState.currentTab = targetedTab;
            
            // A11y
            const tabTitle = button.innerText;
            announceA11y(`Switched to tab ${tabTitle}`);
            
            // Post render handlers
            if (targetedTab === 'map-tab') {
                refreshGatesTraffic();
            } else if (targetedTab === 'eco-tab') {
                refreshLeaderboard();
            } else if (targetedTab === 'command-tab') {
                refreshIncidentsFeed();
            }
        });
    });
}

// 2. Role Swapping Handler
function initRoleSwitcher() {
    roleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const role = button.getAttribute('data-role');
            appState.currentRole = role;
            
            // Update visual selection states
            roleButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-pressed', 'false');
            });
            button.classList.add('active');
            button.setAttribute('aria-pressed', 'true');
            
            // Handle Command Center restrictions display
            const commandRestrictBanner = document.getElementById('command-restrict-banner');
            const btnSubmitIncident = document.getElementById('btn-submit-incident');
            const incidentForm = document.getElementById('incident-form-id');
            
            if (role === 'organizer') {
                if (commandRestrictBanner) commandRestrictBanner.classList.add('hidden');
                if (incidentForm) {
                    const inputs = incidentForm.querySelectorAll('input, select, button');
                    inputs.forEach(el => el.removeAttribute('disabled'));
                }
            } else {
                if (commandRestrictBanner) commandRestrictBanner.classList.remove('hidden');
                if (incidentForm) {
                    const inputs = incidentForm.querySelectorAll('input, select, button');
                    inputs.forEach(el => el.setAttribute('disabled', 'true'));
                }
            }
            
            // Reset chat messages display to match new role
            renderChatHistory();
            loadSuggestedQueries();
            
            // Set labels in chat title
            const chatTitle = document.getElementById('chat-title-id');
            const roleCapitalized = role.charAt(0).toUpperCase() + role.slice(1);
            chatTitle.textContent = `FIFA 2026 Assistant [${roleCapitalized} Context]`;
            
            announceA11y(`Context switched to ${roleCapitalized} mode.`);
        });
    });
}

// 3. Accessibility Adjustment Panel
function initAccessibilityControls() {
    const btnContrast = document.getElementById('btn-contrast-toggle');
    const btnFontDec = document.getElementById('btn-font-decrease');
    const btnFontInc = document.getElementById('btn-font-increase');
    
    btnContrast.addEventListener('click', () => {
        docBody.classList.toggle('high-contrast');
        const enabled = docBody.classList.contains('high-contrast');
        announceA11y(enabled ? "High contrast mode enabled." : "High contrast mode disabled.");
    });
    
    btnFontDec.addEventListener('click', () => {
        if (appState.fontSize > 12) {
            appState.fontSize -= 1;
            docBody.style.setProperty('--base-font-size', `${appState.fontSize}px`);
            announceA11y(`Font size reduced to ${appState.fontSize} pixels.`);
        }
    });
    
    btnFontInc.addEventListener('click', () => {
        if (appState.fontSize < 24) {
            appState.fontSize += 1;
            docBody.style.setProperty('--base-font-size', `${appState.fontSize}px`);
            announceA11y(`Font size increased to ${appState.fontSize} pixels.`);
        }
    });
}

// 4. AI Copilot Chat Interface
function initChatInterface() {
    const chatForm = document.getElementById('chat-form-id');
    const inputQuery = document.getElementById('input-query-id');
    const selectLang = document.getElementById('select-lang-id');
    const checkTts = document.getElementById('check-tts-id');
    const btnStt = document.getElementById('btn-stt-id');
    
    selectLang.addEventListener('change', (e) => {
        appState.language = e.target.value;
        announceA11y(`Assistant output language updated to ${e.target.options[e.target.selectedIndex].text}`);
    });
    
    checkTts.addEventListener('change', (e) => {
        appState.ttsEnabled = e.target.checked;
        announceA11y(appState.ttsEnabled ? "Text to Speech voice synthesis enabled." : "Text to Speech disabled.");
    });
    
    // Voice Dictation Simulation / Live browser recognition
    btnStt.addEventListener('click', () => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = appState.language === 'es' ? 'es-ES' : (appState.language === 'fr' ? 'fr-FR' : 'en-US');
            recognition.start();
            announceA11y("Listening to speech...");
            
            inputQuery.value = "...";
            
            recognition.onresult = (event) => {
                const voiceText = event.results[0][0].transcript;
                inputQuery.value = voiceText;
                announceA11y(`Speech recognized: ${voiceText}`);
            };
            recognition.onerror = () => {
                simulateSttFallback(inputQuery);
            };
        } else {
            simulateSttFallback(inputQuery);
        }
    });
    
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        submitChatQuery(inputQuery.value);
        inputQuery.value = '';
    });
    
    // Load initial query layout
    renderChatHistory();
}

function simulateSttFallback(inputField) {
    announceA11y("Simulating voice recognition standard queries...");
    const options = [
        "Is my bag clear sizing permitted inside MetLife?",
        "How do I access wheelchair ADA routing?",
        "Where is the nearest NJ Transit train station?",
        "Is there sensory bags at guest services?"
    ];
    const pick = options[Math.floor(Math.random() * options.length)];
    let index = 0;
    inputField.value = "";
    
    const interval = setInterval(() => {
        if (index < pick.length) {
            inputField.value += pick[index];
            index++;
        } else {
            clearInterval(interval);
            announceA11y("Voice simulation complete.");
        }
    }, 40);
}

function renderChatHistory() {
    const chatContainer = document.getElementById('chat-history-id');
    chatContainer.innerHTML = '';
    
    const activeHistory = appState.chatHistory[appState.currentRole];
    activeHistory.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.role === 'user' ? 'user-message' : 'model-message'}`;
        
        const senderMeta = document.createElement('div');
        senderMeta.className = 'msg-meta';
        senderMeta.innerText = msg.role === 'user' ? 'You' : `AI Assistant [${appState.currentRole.toUpperCase()}]`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'msg-content';
        contentDiv.innerText = msg.content;
        
        messageDiv.appendChild(senderMeta);
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
    });
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function submitChatQuery(messageText) {
    if (!messageText.trim()) return;
    
    const activeHistory = appState.chatHistory[appState.currentRole];
    
    // 1. Add user message
    activeHistory.push({ role: 'user', content: messageText });
    renderChatHistory();
    announceA11y("Sending message to AI Assistant.");
    
    // Create loading message block
    const chatContainer = document.getElementById('chat-history-id');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message model-message loading-msg';
    loadingDiv.innerHTML = `<span class="msg-meta">AI Assistant</span><div class="msg-content">Thinking... 🧠</div>`;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    try {
        // Map history objects mapping models schema ChatMessage
        const requestHistory = activeHistory.slice(0, -1).map(h => ({
            role: h.role,
            content: h.content
        }));
        
        const response = await fetch('/api/assistant/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_role: appState.currentRole,
                message: messageText,
                history: requestHistory,
                language: appState.language
            })
        });
        
        if (!response.ok) throw new Error("Server responded with error.");
        const data = await response.json();
        
        // Remove loading state
        if (loadingDiv.parentNode) loadingDiv.parentNode.removeChild(loadingDiv);
        
        // 2. Add model response
        activeHistory.push({ role: 'model', content: data.response });
        renderChatHistory();
        
        // Trigger voice synthesis if checked
        if (appState.ttsEnabled) {
            speakSpeechText(data.response);
        }
        
        // Reload suggested actions based on context response
        if (data.suggested_actions) {
            updateSuggestedQueriesUI(data.suggested_actions);
        }
        
        announceA11y("Received response from AI.");
    } catch (err) {
        console.error(err);
        if (loadingDiv.parentNode) loadingDiv.parentNode.removeChild(loadingDiv);
        activeHistory.push({ role: 'model', content: "Sorry, I am having trouble connecting to operations database right now. Please verify your connection." });
        renderChatHistory();
    }
}

function speakSpeechText(text) {
    if ('speechSynthesis' in window) {
        // Cancel ongoing voices
        window.speechSynthesis.cancel();
        const cleanedText = text.replace(/\[.*?\]/g, ""); // Strip any bracketed log details for voice clarity
        const utterance = new SpeechSynthesisUtterance(cleanedText);
        
        // Match language locale
        if (appState.language === 'es') utterance.lang = 'es-ES';
        else if (appState.language === 'fr') utterance.lang = 'fr-FR';
        else utterance.lang = 'en-US';
        
        window.speechSynthesis.speak(utterance);
    }
}

function updateSuggestedQueriesUI(actions) {
    const list = document.getElementById('suggestions-list-id');
    list.innerHTML = '';
    actions.forEach(action => {
        const btn = document.createElement('button');
        btn.className = 'suggested-query-btn';
        btn.innerText = action;
        btn.addEventListener('click', () => {
            submitChatQuery(action);
        });
        list.appendChild(btn);
    });
}

function loadSuggestedQueries() {
    let queries = [];
    if (appState.currentRole === 'fan') {
        queries = ["ADA seating and elevator locations", "NJ Transit Meadowlands train timings", "FIFA Sustainability guidelines"];
    } else if (appState.currentRole === 'volunteer') {
        queries = ["Where is the volunteer check-in hub?", "Emergency intercom layout guideline", "Clear bag security boundaries"];
    } else {
        queries = ["Show active incident summary report", "Reroute crowds away from Gate B", "NJ Transit train operations status"];
    }
    updateSuggestedQueriesUI(queries);
}

// 5. Stadium Gates Traffic & SVG Nodes
function initMapTrafficInterface() {
    const btnRefresh = document.getElementById('btn-refresh-map-id');
    const radioStandard = document.getElementById('radio-standard-id');
    const radioAda = document.getElementById('radio-ada-id');
    
    btnRefresh.addEventListener('click', () => {
        refreshGatesTraffic();
        announceA11y("Stadium gate occupancy status refreshed.");
    });
    
    const updateDirections = () => {
        const directionsBox = document.getElementById('routing-directions-id');
        if (radioAda.checked) {
            directionsBox.innerHTML = `<strong>♿ Wheelchair & ADA routing directions:</strong> Take the elevator at Gate A or Gate C to bypass the primary concourse steps. ADA elevators are marked in blue. Volunteers in neon green vests are stationed at elevator portals to assist.`;
            announceA11y("ADA routing directions selected.");
        } else {
            directionsBox.innerHTML = `<strong>🚶 Standard Pedestrian directions:</strong> Enter via Gate D (South) if arriving by train. Move clockwise around the outer concourse loop. Avoid the Gate B North portal due to scanner congestion limits.`;
            announceA11y("Standard pedestrian directions selected.");
        }
    };
    
    radioStandard.addEventListener('change', updateDirections);
    radioAda.addEventListener('change', updateDirections);
    
    // Set initial
    updateDirections();
}

async function refreshGatesTraffic() {
    try {
        const response = await fetch('/api/operations/gates');
        if (!response.ok) throw new Error();
        const data = await response.json();
        
        // Update Sidebar items
        const gatesList = document.getElementById('gates-list-id');
        gatesList.innerHTML = '';
        
        data.forEach(gate => {
            const sevClass = gate.congestion_level.toLowerCase();
            const widget = document.createElement('div');
            widget.className = `gate-traffic-widget status-${sevClass}`;
            widget.innerHTML = `
                <div class="gate-widget-header">
                    <span class="gate-name-label">${gate.gate}</span>
                    <span class="gate-status-pill ${sevClass}">${gate.congestion_level}</span>
                </div>
                <div class="gate-widget-stats">
                    <span>Wait: <strong>${gate.wait_time_minutes} min</strong></span>
                    <span>Flow: <strong>${gate.current_occupancy}/${gate.max_capacity}</strong></span>
                </div>
            `;
            gatesList.appendChild(widget);
            
            // Update SVG map elements dynamically
            let svgId = "";
            if (gate.gate.includes("A")) svgId = "svg-gate-a";
            else if (gate.gate.includes("B")) svgId = "svg-gate-b";
            else if (gate.gate.includes("C")) svgId = "svg-gate-c";
            else if (gate.gate.includes("D")) svgId = "svg-gate-d";
            
            const circle = document.getElementById(svgId);
            if (circle) {
                circle.className.baseVal = `gate-node node-${sevClass}`;
            }
        });
    } catch (err) {
        console.error("Failed to load gates: ", err);
    }
}

// 6. Sustainability Hub & Waste Calculator
function initSustainabilityInterface() {
    const btnScan = document.getElementById('btn-scan-waste');
    const selectWaste = document.getElementById('select-trash-item');
    const btnClaim = document.getElementById('btn-submit-points');
    
    btnScan.addEventListener('click', async () => {
        const itemId = selectWaste.value;
        if (!itemId) {
            announceA11y("Please select a waste item category first.");
            return;
        }
        
        try {
            const response = await fetch('/api/sustainability/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: itemId })
            });
            if (!response.ok) throw new Error();
            const data = await response.json();
            
            // Show result card
            const resultCard = document.getElementById('scan-result-id');
            resultCard.classList.remove('hidden');
            
            document.getElementById('scan-item-name').innerText = data.item_name;
            
            // Bin styling
            const binBadge = document.getElementById('scan-bin-badge');
            binBadge.innerText = data.target_bin;
            binBadge.className = 'bin-badge';
            if (data.target_bin.includes("Recycle")) binBadge.classList.add('recycle');
            else if (data.target_bin.includes("Compost")) binBadge.classList.add('compost');
            else binBadge.classList.add('landfill');
            
            document.getElementById('scan-instructions').innerText = data.sorting_instruction;
            document.getElementById('scan-co2').innerText = `${data.co2_saved_kg} kg`;
            document.getElementById('scan-points').innerText = data.points_awarded;
            document.getElementById('scan-tip').innerText = data.sustainability_tip;
            
            // Cache point data on the button attributes for easy recovery
            btnClaim.setAttribute('data-points', data.points_awarded);
            btnClaim.setAttribute('data-co2', data.co2_saved_kg);
            
            announceA11y(`Scanning complete. Recommended bin is ${data.target_bin}.`);
        } catch (err) {
            console.error(err);
        }
    });
    
    btnClaim.addEventListener('click', async () => {
        const username = document.getElementById('username-points').value.trim();
        const points = parseInt(btnClaim.getAttribute('data-points') || 0);
        const co2 = parseFloat(btnClaim.getAttribute('data-co2') || 0);
        
        if (!username) {
            alert("Please enter a username.");
            return;
        }
        
        try {
            const response = await fetch(`/api/sustainability/add-points?username=${encodeURIComponent(username)}&points=${points}&co2_saved_kg=${co2}`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error();
            const resData = await response.json();
            
            // Update global screen counters
            document.getElementById('global-eco-points').innerText = resData.current_stadium_points.toLocaleString();
            document.getElementById('global-co2-saved').innerText = `${resData.current_stadium_co2_saved.toFixed(1)} kg`;
            
            // Clear scanning state
            document.getElementById('scan-result-id').classList.add('hidden');
            selectWaste.value = '';
            
            // Reload leaderboard
            refreshLeaderboard();
            announceA11y(`Points claimed successfully for ${username}. Leaderboard updated.`);
        } catch (err) {
            console.error(err);
        }
    });
}

async function refreshLeaderboard() {
    try {
        const response = await fetch('/api/sustainability/leaderboard');
        if (!response.ok) throw new Error();
        const data = await response.json();
        
        const body = document.getElementById('leaderboard-body-id');
        body.innerHTML = '';
        
        data.leaderboard.forEach((entry, idx) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>#${idx + 1}</strong></td>
                <td>${entry.username}</td>
                <td>${entry.points}</td>
                <td>${entry.co2_saved_kg.toFixed(1)} kg</td>
            `;
            body.appendChild(row);
        });
    } catch (err) {
        console.error(err);
    }
}

// 7. Command Center Dashboard
function initCommandCenterInterface() {
    const incidentForm = document.getElementById('incident-form-id');
    
    incidentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (appState.currentRole !== 'organizer') {
            alert("Access Denied: Only organizers are authorized to submit operations tickets.");
            return;
        }
        
        const title = document.getElementById('input-incident-title').value.trim();
        const zone = document.getElementById('select-incident-zone').value.trim();
        const severity = document.getElementById('select-incident-severity').value;
        const description = document.getElementById('input-incident-desc').value.trim();
        
        try {
            const response = await fetch('/api/operations/incidents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, zone, severity, description })
            });
            
            if (!response.ok) throw new Error();
            
            incidentForm.reset();
            refreshIncidentsFeed();
            announceA11y("Incident logged successfully.");
        } catch (err) {
            console.error(err);
        }
    });
}

async function refreshIncidentsFeed() {
    try {
        const response = await fetch('/api/operations/incidents');
        if (!response.ok) throw new Error();
        const data = await response.json();
        
        // Count
        const countSpan = document.getElementById('active-alerts-count-id');
        countSpan.innerText = `${data.length} Active Tickets`;
        
        const list = document.getElementById('alerts-feed-list-id');
        list.innerHTML = '';
        
        data.forEach(inc => {
            const sev = inc.severity.toLowerCase();
            const card = document.createElement('div');
            card.className = 'alert-item-card';
            card.innerHTML = `
                <div class="alert-details">
                    <div class="alert-title-row">
                        <span class="alert-id">${inc.id}</span>
                        <span class="alert-title">${inc.title}</span>
                        <span class="alert-sev-pill ${sev}">${inc.severity}</span>
                    </div>
                    <span class="alert-zone-desc">📍 Location: ${inc.zone}</span>
                    <p class="alert-desc-detail">${inc.description}</p>
                </div>
                <div class="alert-item-actions">
                    <button class="btn-primary btn-plan-action" data-id="${inc.id}">Draft Plan ⚙️</button>
                    <button class="btn-secondary btn-resolve-action" data-id="${inc.id}">Resolve</button>
                </div>
            `;
            list.appendChild(card);
        });
        
        // Attach card actions
        document.querySelectorAll('.btn-plan-action').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                generateIncidentAIPlan(id);
            });
        });
        
        document.querySelectorAll('.btn-resolve-action').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                resolveIncidentTicket(id);
            });
        });
    } catch (err) {
        console.error(err);
    }
}

async function generateIncidentAIPlan(incidentId) {
    const displayPanel = document.getElementById('decision-support-content-id');
    displayPanel.innerHTML = '<div class="empty-state">Drafting operations layout via GenAI... 🤖</div>';
    announceA11y("Drafting operational recovery instructions from Gemini.");
    
    try {
        const response = await fetch(`/api/operations/incidents/${incidentId}/ai-plan`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error();
        const data = await response.json();
        
        // Build beautiful HTML presentation structure for decisions
        let tasksHtml = '';
        data.assigned_tasks.forEach(t => {
            tasksHtml += `<li>${t}</li>`;
        });
        
        displayPanel.innerHTML = `
            <div class="ai-plan-container">
                <div>
                    <h4 class="ai-section-title">Incident Assessment & Resolution Plan</h4>
                    <p class="ai-text">${data.response_plan}</p>
                </div>
                
                <div>
                    <h4 class="ai-section-title">Volunteer Task Dispatch</h4>
                    <ul class="tasks-list">
                        ${tasksHtml}
                    </ul>
                </div>
                
                <div>
                    <h4 class="ai-section-title">Multilingual Safety Announcements</h4>
                    <div class="announcements-tab-wrapper">
                        <strong>English:</strong>
                        <p class="announcement-box">${data.announcements.en}</p>
                        <strong>Español:</strong>
                        <p class="announcement-box">${data.announcements.es}</p>
                        <strong>Français:</strong>
                        <p class="announcement-box">${data.announcements.fr}</p>
                    </div>
                </div>
            </div>
        `;
        
        announceA11y("Incident plan loaded in operations dashboard.");
    } catch (err) {
        console.error(err);
        displayPanel.innerHTML = '<div class="empty-state text-danger">Failed to generate operations layout. Switch roles and try again.</div>';
    }
}

async function resolveIncidentTicket(incidentId) {
    if (appState.currentRole !== 'organizer') {
        alert("Access Denied: Only organizers are authorized to close operations tickets.");
        return;
    }
    
    try {
        const response = await fetch(`/api/operations/incidents/${incidentId}/resolve`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error();
        
        // Clear AI Panel if resolving that incident
        const displayPanel = document.getElementById('decision-support-content-id');
        displayPanel.innerHTML = `
            <div class="empty-state">
                <p>Select an operational ticket from the feed and click <strong>"Draft Response Plan"</strong> to generate real-time dispatch solutions, multilingual announcements, and task updates.</p>
            </div>
        `;
        
        refreshIncidentsFeed();
        announceA11y(`Incident ticket ${incidentId} marked as resolved.`);
    } catch (err) {
        console.error(err);
    }
}
