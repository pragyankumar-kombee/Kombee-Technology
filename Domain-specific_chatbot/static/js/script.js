const chatBox = document.getElementById("chatBox");
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("messageInput");
const clearBtn = document.getElementById("clearBtn");
const actionsBtn = document.getElementById("actionsBtn");
const closePanelBtn = document.getElementById("closePanelBtn");
const addSectionBtn = document.getElementById("addSectionBtn");
const modelStatus = document.getElementById("modelStatus");
const actionPanel = document.getElementById("actionPanel");
const panelOverlay = document.createElement("div");
const sectionsList = document.getElementById("sectionsList");

panelOverlay.classList.add("panel-overlay");
document.body.appendChild(panelOverlay);

// Create typing indicator element
const typingDiv = document.createElement("div");
typingDiv.classList.add("typing-indicator", "message", "bot");
typingDiv.innerHTML = `<span></span><span></span><span></span>`;
typingDiv.id = "typingIndicator";
typingDiv.style.display = "none";
if (chatBox) chatBox.appendChild(typingDiv);

// Action panel state
let sections = [];
let editingSectionId = null;

function formatText(text) {
    if (typeof text !== 'string') text = String(text || '');
    return text.replace(/\n/g, '<br>');
}

function addMessage(text, type) {
    try {
        const messageWrapper = document.createElement("div");
        messageWrapper.classList.add("message", type);
        
        // Add avatar/name
        const nameDiv = document.createElement("div");
        nameDiv.classList.add("message-avatar");
        nameDiv.innerHTML = type === 'user' ? `<i class='bx bx-user'></i> You` : `<i class='bx bx-bot'></i> Assistant`;
        
        const contentDiv = document.createElement("div");
        contentDiv.innerHTML = formatText(text);
        
        messageWrapper.appendChild(nameDiv);
        messageWrapper.appendChild(contentDiv);
        
        if (typingDiv.parentNode === chatBox) {
            chatBox.insertBefore(messageWrapper, typingDiv);
        } else {
            chatBox.appendChild(messageWrapper);
        }
        
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (e) {
        console.error("Error adding message:", e);
    }
}

function showTyping() {
    chatBox.appendChild(typingDiv);
    typingDiv.style.display = "block";
    chatBox.scrollTop = chatBox.scrollHeight;
    sendBtn.disabled = true;
    messageInput.disabled = true;
}

function hideTyping() {
    typingDiv.style.display = "none";
    sendBtn.disabled = false;
    messageInput.disabled = false;
    messageInput.focus();
}

async function checkModelStatus() {
    try {
        const response = await fetch("/model-info");
        const data = await response.json();
        if (data.loaded) {
            modelStatus.innerText = "Online";
            modelStatus.previousElementSibling.style.background = "#10b981";
            modelStatus.previousElementSibling.style.boxShadow = "0 0 10px #10b981";
        } else {
            modelStatus.innerText = "Loading...";
            modelStatus.previousElementSibling.style.background = "#f59e0b";
            modelStatus.previousElementSibling.style.boxShadow = "0 0 10px #f59e0b";
            setTimeout(checkModelStatus, 2000);
        }
    } catch (e) {
        modelStatus.innerText = "Error";
        modelStatus.previousElementSibling.style.background = "#ef4444";
        modelStatus.previousElementSibling.style.boxShadow = "0 0 10px #ef4444";
    }
}

let isSending = false;

async function sendMessage() {
    const message = messageInput.value.trim();
    if (message === "" || isSending) return;

    addMessage(message, "user");
    messageInput.value = "";
    
    showTyping();
    isSending = true;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        hideTyping();
        isSending = false;

        if (response.status === 202) {
            addMessage("Model is still loading. Please wait a moment and try again.", "bot");
            checkModelStatus();
        } else if (data.response) {
            addMessage(data.response, "bot");
        } else if (data.error) {
            addMessage(`Error: ${data.error}`, "bot");
        }
    } catch (error) {
        hideTyping();
        isSending = false;
        addMessage("Error contacting server. Please ensure the backend is running.", "bot");
    }
}

sendBtn.onclick = sendMessage;

let typeTimer;
messageInput.addEventListener("input", function() {
    clearTimeout(typeTimer);
    typeTimer = setTimeout(() => {
        if (messageInput.value.trim().length > 0) {
            sendBtn.style.opacity = "1";
        } else {
            sendBtn.style.opacity = "0.6";
        }
    }, 100);
});

messageInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

clearBtn.onclick = async function () {
    try {
        await fetch("/clear", { method: "POST" });
        chatBox.innerHTML = "";
        chatBox.appendChild(typingDiv);
    } catch (e) {
        console.error("Failed to clear history", e);
    }
};

async function loadHistory() {
    try {
        const response = await fetch("/history");
        const data = await response.json();
        
        if (typingDiv.parentNode !== chatBox) chatBox.appendChild(typingDiv);

        if (data.history && data.history.length > 0) {
            data.history.forEach(msg => {
                if (msg.user) addMessage(msg.user, "user");
                if (msg.assistant) addMessage(msg.assistant, "bot");
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    } catch (e) {
        console.error("Failed to load history", e);
    }
}

// Action Panel Functions
function openPanel() {
    actionPanel.classList.add("open");
    panelOverlay.classList.add("open");
    loadSections();
}

function closePanel() {
    actionPanel.classList.remove("open");
    panelOverlay.classList.remove("open");
    editingSectionId = null;
}

async function loadSections() {
    try {
        const response = await fetch('/sections');
        const data = await response.json();
        sections = data.sections || [];
        if (sections.length === 0) {
            // Default sections
            sections = [
                { id: 'general', title: 'General', content: 'General conversation and information' },
                { id: 'notes', title: 'Notes', content: 'Store important notes and reminders' },
                { id: 'tasks', title: 'Tasks', content: 'Track your tasks and to-do list' }
            ];
            saveSections();
        }
        renderSections();
    } catch (e) {
        console.error("Failed to load sections", e);
        // Fallback to localStorage
        const storedSections = localStorage.getItem('nexus_sections');
        if (storedSections) {
            sections = JSON.parse(storedSections);
        } else {
            sections = [
                { id: 'general', title: 'General', content: 'General conversation and information' },
                { id: 'notes', title: 'Notes', content: 'Store important notes and reminders' },
                { id: 'tasks', title: 'Tasks', content: 'Track your tasks and to-do list' }
            ];
        }
        renderSections();
    }
}

async function saveSections() {
    try {
        await fetch('/sections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sections: sections })
        });
    } catch (e) {
        console.error("Failed to save sections", e);
        localStorage.setItem('nexus_sections', JSON.stringify(sections));
    }
}

function renderSections() {
    sectionsList.innerHTML = '';
    
    sections.forEach(section => {
        const sectionCard = document.createElement('div');
        sectionCard.className = 'section-card';
        sectionCard.innerHTML = `
            <div class="section-header">
                <div class="section-title">${section.title}</div>
                <div class="section-actions">
                    <button class="edit" onclick="editSection('${section.id}')" title="Edit">
                        <i class='bx bx-edit'></i>
                    </button>
                    <button class="delete" onclick="deleteSection('${section.id}')" title="Delete">
                        <i class='bx bx-trash'></i>
                    </button>
                </div>
            </div>
            <div class="section-content">${section.content}</div>
        `;
        sectionsList.appendChild(sectionCard);
    });
}

function deleteSection(id) {
    if (confirm('Are you sure you want to delete this section?')) {
        sections = sections.filter(s => s.id !== id);
        saveSections();
        renderSections();
    }
}

function editSection(id) {
    const section = sections.find(s => s.id === id);
    if (section) {
        showEditModal(section);
    }
}

function showEditModal(section = null) {
    const modal = document.createElement('div');
    modal.className = 'modal open';
    
    const isEditing = section !== null;
    const title = isEditing ? 'Edit Section' : 'Add New Section';
    const actionBtn = isEditing ? 'Update' : 'Add Section';
    
    modal.innerHTML = `
        <h3>${title}</h3>
        <input type="text" id="sectionTitle" placeholder="Section title" value="${section ? section.title : ''}">
        <textarea id="sectionContent" placeholder="Section content/description">${section ? section.content : ''}</textarea>
        <div class="modal-actions">
            <button class="secondary" onclick="this.closest('.modal').remove()">Cancel</button>
            <button class="primary" onclick="saveSection('${section ? section.id : ''}', this)">${actionBtn}</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

window.saveSection = function(id, btn) {
    const title = document.getElementById('sectionTitle').value.trim();
    const content = document.getElementById('sectionContent').value.trim();
    
    if (!title) {
        alert('Please enter a section title');
        return;
    }
    
    if (id) {
        // Edit existing
        const index = sections.findIndex(s => s.id === id);
        if (index !== -1) {
            sections[index].title = title;
            sections[index].content = content;
        }
    } else {
        // Add new
        const newSection = {
            id: Date.now().toString(),
            title: title,
            content: content
        };
        sections.push(newSection);
    }
    
    saveSections();
    renderSections();
    document.querySelector('.modal').remove();
};

window.editSection = function(id) {
    editSection(id);
};

window.deleteSection = function(id) {
    deleteSection(id);
};

actionsBtn.onclick = openPanel;
closePanelBtn.onclick = closePanel;
panelOverlay.onclick = closePanel;
addSectionBtn.onclick = () => showEditModal(null);

// Initial loads
loadHistory();
checkModelStatus();