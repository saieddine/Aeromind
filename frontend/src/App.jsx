import { useState } from 'react'
import './App.css'
import AircraftViewer from './components/AircraftViewer/AircraftViewer'
import ModelViewer from './components/ModelViewer/ModelViewer'

function App() {
const [currentScreen, setCurrentScreen] = useState('login')
const [userName, setUserName] = useState('')
const [loginName, setLoginName] = useState('')
const [loginPassword, setLoginPassword] = useState('')
const [selectedManufacturer, setSelectedManufacturer] = useState(null)
const [selectedAircraft, setSelectedAircraft] = useState(null)
const [chatInput, setChatInput] = useState('')
const [messages, setMessages] = useState([])
const [chatHistory, setChatHistory] = useState([])
const [activeChatId, setActiveChatId] = useState(null)

const [showFullHistory, setShowFullHistory] = useState(false)
  const [isExplorerOpen, setIsExplorerOpen] = useState(false)
  const [showSystemsImage, setShowSystemsImage] = useState(false)
  const [selectedModel, setSelectedModel] = useState(null)

    const handleLogin = (event) => {
    event.preventDefault()

    if (!loginName.trim() || !loginPassword.trim()) {
      return
    }

    setUserName(loginName.trim())
    setCurrentScreen('home')
  }

  const openManufacturer = (manufacturer) => {
    setSelectedManufacturer(manufacturer)
    setSelectedAircraft(null)
    setCurrentScreen('aircraft')
  }

  const openAircraft = (aircraft) => {
    setSelectedAircraft(aircraft)

    if (aircraft === 'A320') {
      setCurrentScreen('a320')
    } else {
      setCurrentScreen('placeholder')
    }
  }

  const scrollToOverview = () => {
    const section = document.getElementById('overview')

    if (section) {
      section.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const startNewChat = () => {
  const newChat = {
    id: Date.now(),
    title: 'New chat',
    messages: [],
  }

  
const sendMessage = (event) => {
  event.preventDefault()

  const text = chatInput.trim()
  if (!text) return

  let chatId = activeChatId
  let updatedHistory = [...chatHistory]

  if (chatId === null) {
    chatId = Date.now()

    updatedHistory = [
      {
        id: chatId,
        title: text.length > 30 ? text.slice(0, 30) + '...' : text,
        messages: [],
      },
      ...updatedHistory,
    ]
  }

  const userMessage = {
    role: 'user',
    content: text,
  }

  const existingChat = updatedHistory.find(
    (chat) => chat.id === chatId
  )

  const updatedMessages = [
    ...(existingChat ? existingChat.messages : []),
    userMessage,
  ]

  updatedHistory = updatedHistory.map((chat) =>
    chat.id === chatId
      ? {
          ...chat,
          title:
            chat.title === 'New chat'
              ? text.length > 30
                ? text.slice(0, 30) + '...'
                : text
              : chat.title,
          messages: updatedMessages,
        }
      : chat
  )

  setChatHistory(updatedHistory)
  setActiveChatId(chatId)
  setMessages(updatedMessages)
  setChatInput('')
}

const deleteChat = (chatId) => {
console.log('Deleting chat:', chatId)

  const updatedHistory = chatHistory.filter(
    (chat) => chat.id !== chatId
  )

  setChatHistory(updatedHistory)

  if (activeChatId === chatId) {
    setActiveChatId(null)
    setMessages([])
    setChatInput('')
  }
}


  setChatHistory((previousChats) => [newChat, ...previousChats])
  setActiveChatId(newChat.id)
  setMessages([])
  setChatInput('')
  setCurrentScreen('assistant')
}


return (
  <>
    {currentScreen === 'login' ? (
      
/*Login Screen*/
<main className="login-screen">
  <div className="login-panel">
    <div className="login-brand">
      <span className="login-brand-mark">A</span>
      <span>AEROMIND</span>
    </div>

    <p className="eyebrow">AIRCRAFT INTELLIGENCE PLATFORM</p>

    <h1>
      Explore beyond
      <br />
      the surface.
    </h1>

    <p className="login-description">
      Discover aircraft, explore engineering systems,
      and understand aviation through intelligent exploration.
    </p>

    <form className="login-form" onSubmit={handleLogin}>
      <label htmlFor="login-name">USERNAME</label>
      <input
        id="login-name"
        type="text"
        value={loginName}
        onChange={(event) => setLoginName(event.target.value)}
        placeholder="Enter your username"
        required
      />

      <label htmlFor="login-password">PASSWORD</label>
      <input
        id="login-password"
        type="password"
        value={loginPassword}
        onChange={(event) => setLoginPassword(event.target.value)}
        placeholder="Enter your password"
        required
      />

      <button type="submit" className="login-submit">
        Enter AeroMind <span>↗</span>
      </button>
    </form>

    <p className="login-footer">
      AEROMIND <span>/</span> AVIATION EXPLORATION
    </p>
  </div>
</main>

    ) : currentScreen === 'home' ? (

/*Home Screen*/   
<main className="dashboard">
  <aside className="sidebar">
    <div className="sidebar-brand">
      <span className="login-brand-mark">A</span>
      <span>AEROMIND</span>
    </div>

    <p className="sidebar-label">WORKSPACE</p>

    <button
      className="sidebar-link active"
      onClick={() => setCurrentScreen('home')}
    >
      <span>⌂</span> Overview
    </button>

    <button
      className="sidebar-link"
      onClick={() => setCurrentScreen('manufacturer')}
    >
      <span>✈</span> Aircraft
    </button>

    <button
      className="sidebar-link"
      onClick={() => alert('AI Assistant will be added later.')}
    >
      <span>✳</span> AI Assistant
    </button>

    <button
      className="sidebar-link"
      onClick={() => alert('What-If tools will be added later.')}
    >
      <span>◈</span> What-If
    </button>

    <div className="sidebar-bottom">
      <div className="user-avatar">
        {userName.charAt(0).toUpperCase()}
      </div>
      <div>
        <strong>{userName}</strong>
        <p>Explorer</p>
      </div>
    </div>
  </aside>

  <section className="dashboard-main">
    <header className="dashboard-topbar">
      <span>WORKSPACE / OVERVIEW</span>
      <span>AVIATION INTELLIGENCE PLATFORM</span>
    </header>

    <div className="dashboard-content">
      <p className="eyebrow">YOUR AVIATION WORKSPACE</p>

      <h1>
        Welcome to AeroMind,
        <br />
        {userName}.
      </h1>

      <p className="dashboard-description">
        Explore aircraft engineering, discover technical systems,
        and understand the machines that shape modern aviation.
      </p>

      <button
        className="dashboard-feature"
        onClick={() => setCurrentScreen('manufacturer')}
      >
        <div className="feature-icon">✈</div>

        <div className="feature-text">
          <p className="eyebrow">AIRCRAFT LIBRARY / 01</p>
          <h3>Aircraft Explorer</h3>
          <p>
            Browse manufacturers, explore aircraft families,
            and enter the technical world of individual aircraft.
          </p>
        </div>

        <span className="feature-arrow">↗</span>
      </button>

      <div className="dashboard-bottom-grid">
        <div className="dashboard-info-card">
          <p className="eyebrow">02 / INTELLIGENCE</p>
          <h3>AI Assistant</h3>
          <p>Ask questions about aircraft and aviation systems.</p>
          <span>COMING LATER</span>
        </div>

        <div className="dashboard-info-card">
          <p className="eyebrow">03 / SIMULATION</p>
          <h3>What-If</h3>
          <p>Explore hypothetical aircraft scenarios.</p>
          <span>COMING LATER</span>
        </div>
      </div>
    </div>
  </section>
</main>

  
) : currentScreen === 'manufacturer' ? (
  <main className="selection-screen">
    <header className="selection-header">
      <button
        className="selection-back"
        onClick={() => setCurrentScreen('home')}
      >
        ← Back to Overview
      </button>
      <span className="selection-label">AEROMIND / AIRCRAFT LIBRARY</span>
    </header>

    <section className="selection-content">
      <p className="eyebrow">AIRCRAFT EXPLORER</p>
      <h1>Explore the aircraft world.</h1>
      <p className="selection-description">
        Select a manufacturer to explore its aircraft families
        and discover the engineering behind each aircraft.
      </p>

      <div className="manufacturer-grid">
        <button
          className={`manufacturer-card ${selectedManufacturer === 'Airbus' ? 'selected' : ''}`}
          onClick={() => setSelectedManufacturer('Airbus')}
        >
          <span className="manufacturer-number">01 / MANUFACTURER</span>
          <span className="manufacturer-name">AIRBUS</span>
          <span className="manufacturer-detail">European aerospace manufacturer</span>
          <span className="manufacturer-arrow">↗</span>
        </button>

        <button
          className={`manufacturer-card ${selectedManufacturer === 'Boeing' ? 'selected' : ''}`}
          onClick={() => setSelectedManufacturer('Boeing')}
        >
          <span className="manufacturer-number">02 / MANUFACTURER</span>
          <span className="manufacturer-name">BOEING</span>
          <span className="manufacturer-detail">American aerospace manufacturer</span>
          <span className="manufacturer-arrow">↗</span>
        </button>
      </div>

      {selectedManufacturer && (
        <section className="aircraft-family-section">
          <p className="eyebrow">{selectedManufacturer.toUpperCase()} / AIRCRAFT FAMILIES</p>
          <h2>Select an aircraft family</h2>

          {selectedManufacturer === 'Airbus' ? (
            <div className="aircraft-family-grid">
              {['A320', 'A220', 'A330', 'A350', 'A380'].map((aircraft) => (
                <button
                  className="aircraft-family-card"
                  key={aircraft}
                  onClick={() => openAircraft(aircraft)}
                >
                  <span className="family-code">{aircraft}</span>
                  <span className="family-description">
                    {aircraft === 'A320'
                      ? 'Single-aisle aircraft'
                      : aircraft === 'A220'
                      ? 'Small single-aisle aircraft'
                      : aircraft === 'A330'
                      ? 'Wide-body aircraft'
                      : aircraft === 'A350'
                      ? 'Long-range wide-body aircraft'
                      : 'Double-deck wide-body aircraft'}
                  </span>
                  <span className="family-arrow">↗</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="aircraft-family-grid">
              {['737', '747', '767', '777', '787'].map((aircraft) => (
                <button
                  className="aircraft-family-card"
                  key={aircraft}
                  onClick={() => openAircraft(aircraft)}
                >
                  <span className="family-code">Boeing {aircraft}</span>
                  <span className="family-description">Commercial aircraft family</span>
                  <span className="family-arrow">↗</span>
                </button>
              ))}
            </div>
          )}
        </section>
      )}
    </section>
  </main>




) : currentScreen === 'assistant' ? (
  <main className="assistant-screen">
    <aside className="chat-sidebar">
      <div className="chat-sidebar-brand">
        <span className="login-brand-mark">A</span>
        <span>AEROMIND</span>
      </div>

      <button
  className="new-chat-button"
  onClick={startNewChat}
>
  <span>＋</span> New chat
</button>

      <p className="chat-sidebar-label">WORKSPACE</p>

      <button
        className="chat-sidebar-link"
        onClick={() => setCurrentScreen('manufacturer')}
      >
        <span>✈</span> Aircraft Explorer
      </button>

      <p className="chat-sidebar-label">YOUR CHATS</p>


<div className="chat-history-list">
  {chatHistory.map((chat) => (
    <div
      key={chat.id}
      className={`chat-history-item ${
        activeChatId === chat.id ? 'active' : ''
      }`}
      onClick={() => {
        setActiveChatId(chat.id)
        setMessages(chat.messages)
        setChatInput('')
        setCurrentScreen('assistant')
      }}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.target !== event.currentTarget) return

        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          setActiveChatId(chat.id)
          setMessages(chat.messages)
          setChatInput('')
          setCurrentScreen('assistant')
        }
      }}
    >
      <span className="chat-history-icon">▱</span>

      <span className="chat-history-title">{chat.title}</span>

      
<button
  type="button"
  className="delete-chat-button"
  title="Delete conversation"
  aria-label={`Delete ${chat.title}`}
  onClick={(event) => {
    event.stopPropagation()
    deleteChat(chat.id)
  }}
>
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M3 6h18" />
    <path d="M8 6V4h8v2" />
    <path d="m19 6-1 14H6L5 6" />
    <path d="M10 11v5M14 11v5" />
  </svg>
</button>
    </div>
  ))}
</div>


      <div className="chat-sidebar-bottom">
        <span className="chat-context-dot"></span>
        <div>
          <strong>Airbus A320</strong>
          <p>Aircraft knowledge assistant</p>
        </div>
      </div>
    </aside>

    <section className="chat-main">
      <header className="chat-topbar">
        <span>ASK THE AIRBUS</span>
        <span className="chat-model-label">AEROMIND INTELLIGENCE</span>
      </header>

      <div className="chat-home">
        <div className="chat-home-heading">
          <p className="eyebrow">AEROMIND / AIRBUS A320</p>
          <h1>What would you like to know?</h1>
          <p>
            Ask about aircraft systems, engineering, or technical documentation.
          </p>
        </div>

        <div className="chat-suggestions">
          <button
            onClick={() => setChatInput('How does the A320 hydraulic system work?')}
          >
            <span className="suggestion-icon">↗</span>
            <span>
              <strong>Hydraulic systems</strong>
              <small>How does the A320 hydraulic system work?</small>
            </span>
          </button>

          <button
            onClick={() => setChatInput('Explain the A320 flight control system.')}
          >
            <span className="suggestion-icon">↗</span>
            <span>
              <strong>Flight controls</strong>
              <small>How does the aircraft control its movement?</small>
            </span>
          </button>

          <button
            onClick={() => setChatInput('Explain the A320 electrical system.')}
          >
            <span className="suggestion-icon">↗</span>
            <span>
              <strong>Electrical systems</strong>
              <small>How is electrical power distributed?</small>
            </span>
          </button>

          <button
            onClick={() => setChatInput('What documents are available for the A320?')}
          >
            <span className="suggestion-icon">↗</span>
            <span>
              <strong>Technical documents</strong>
              <small>Find information in aircraft documentation.</small>
            </span>
          </button>
        </div>
      </div>

      <div className="chat-composer-area">
        <form
          className="chat-composer"
          onSubmit={(event) => {
            event.preventDefault()
            if (!chatInput.trim()) return
            alert('Your message is ready. We will connect the RAG backend next.')
          }}
        >
          <textarea
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            placeholder="Ask anything about the Airbus A320..."
            aria-label="Message ASK THE AIRBUS"
            rows={1}
          />
          <button
            type="submit"
            disabled={!chatInput.trim()}
            aria-label="Send message"
          >
            ↑
          </button>
        </form>
        <p className="chat-composer-note">
          AeroMind can make mistakes. Verify critical technical information against official documentation.
        </p>
      </div>
    </section>
  </main>

) : currentScreen === 'placeholder' ? (
  <main className="placeholder-screen">
    <header className="selection-header">
      <button
        className="selection-back"
        onClick={() => setCurrentScreen('manufacturer')}
      >
        ← Back to Aircraft Explorer
      </button>
      <span className="selection-label">AEROMIND / AIRCRAFT LIBRARY</span>
    </header>

    <section className="placeholder-content">
      <p className="eyebrow">AIRCRAFT DEVELOPMENT</p>
      <h1>{selectedManufacturer} {selectedAircraft}</h1>
      <p className="placeholder-status">COMING SOON</p>
      <p className="placeholder-description">
        This aircraft is part of the AeroMind roadmap.
        Its technical exploration experience is currently in development.
      </p>

      <button
        className="placeholder-button"
        onClick={() => setCurrentScreen('manufacturer')}
      >
        Explore other aircraft <span>↗</span>
      </button>
    </section>
  </main>

    ) : (
      <main className="app">
        <nav className="navbar">
<div className="logo">AEROMIND</div>

    
<div className="nav-links">
  <button onClick={() => setCurrentScreen('manufacturer')}>
    Aircraft
  </button>
  <button onClick={() => setCurrentScreen('assistant')}>
    AI Assistant
  </button>
  <button onClick={() => alert('What-If Simulation is coming soon.')}>
    What-If
  </button>
</div>

  </nav>

  <section className="hero">
    <div className="hero-text">
      <p className="eyebrow">AIRBUS A320 FAMILY</p>

      <h1>
        The aircraft
        <br />
        that changed
        <br />
        aviation.
      </h1>

      <p className="description">
        Explore the Airbus A320 through its design, history,
        systems and components. AeroMind helps you understand
        what happens behind the aircraft.
      </p>

      <button className="start-button" onClick={() => setCurrentScreen('assistant')}>
        Ask AEROMIND
      </button>
    </div>

    <div className="aircraft-viewer">
      <AircraftViewer />

      <div className="viewer-label">
        <span>INTERACTIVE 3D MODEL</span>
        <span>DRAG TO ROTATE - SCROLL TO ZOOM</span>
      </div>
      <button
  className="technical-explorer-button"
onClick={() => setIsExplorerOpen(true)}
>
  Explore Aircraft Systems <span>↗</span>
</button>
    </div>
  </section>

  <section className="section overview" id="overview">
    <div className="section-heading">
      <p className="eyebrow">THE A320</p>

      <h2>
        One aircraft.
        <br />
        Decades of innovation.
      </h2>
    </div>

    <div className="overview-content">
      <p className="large-text">
        The Airbus A320 is one of the most recognizable
        commercial aircraft in the world.
      </p>

      <p className="body-text">
        Introduced in the late 1980s, the A320 became the
        foundation of one of the most successful aircraft
        families in aviation. It was designed for short
        and medium haul routes and introduced advanced
        digital flight control technology to commercial
        aviation.
      </p>
    </div>
  </section>

  
<section className="section specifications">
  <div className="section-heading">
    <p className="eyebrow">AIRCRAFT DATA / 01</p>
    <h2>A320 specifications</h2>
    <p className="specifications-description">
      Key dimensions, performance figures and aircraft characteristics.
    </p>
  </div>

  <div className="spec-grid">
    <div className="spec">
      <span><i>01</i> FIRST FLIGHT</span>
      <strong>1987</strong>
    </div>

    <div className="spec">
      <span><i>02</i> PASSENGER CAPACITY</span>
      <strong>180 <small>passengers</small></strong>
    </div>

    <div className="spec">
      <span><i>03</i> RANGE</span>
      <strong>6,200 <small>km</small></strong>
    </div>

    <div className="spec">
      <span><i>04</i> CRUISE SPEED</span>
      <strong>Mach 0.78</strong>
    </div>

    <div className="spec">
      <span><i>05</i> LENGTH</span>
      <strong>37.57 <small>m</small></strong>
    </div>

    <div className="spec">
      <span><i>06</i> WINGSPAN</span>
      <strong>35.80 <small>m</small></strong>
    </div>
  </div>
</section>

  <section className="section history">
    <div className="section-heading">
      <p className="eyebrow">THE STORY</p>

      <h2>
        From 1987
        <br />
        to today.
      </h2>
    </div>
<div className="timeline">
  {/* Always visible: first two milestones */}
  <div className="timeline-item">
    <span>1984</span>
    <div>
      <h3>Development begins</h3>
      <p>
        Airbus begins developing a new generation
        of narrow-body aircraft focused on efficiency,
        technology and passenger comfort.
      </p>
    </div>
  </div>

  <div className="timeline-item">
    <span>1987</span>
    <div>
      <h3>First flight</h3>
      <p>
        The first Airbus A320 takes to the sky,
        marking the beginning of a new generation
        of commercial aircraft.
      </p>
    </div>
  </div>

  {/* Hidden until the visitor clicks the button */}
  {showFullHistory && (
    <>
      <div className="timeline-item">
        <span>1988</span>
        <div>
          <h3>Commercial service</h3>
          <p>
            The A320 enters airline service and begins
            operating commercial passenger flights.
          </p>
        </div>
      </div>

      <div className="timeline-item">
        <span>TODAY</span>
        <div>
          <h3>A global aircraft family</h3>
          <p>
            The A320 family has become one of the most
            widely operated commercial aircraft families
            in the world.
          </p>
        </div>
      </div>
    </>
  )}
</div>

<button
  className="see-more-button"
  onClick={() => setShowFullHistory(!showFullHistory)}
>
  {showFullHistory ? 'See less ↑' : 'See full history ↓'}
</button>
  </section>



  <section className="section components">
    <div className="section-heading">
      <p className="eyebrow">EXPLORE</p>

      <h2>Look closer.</h2>

      <p className="section-description">
        Explore important components of the A320 and
        understand how they contribute to the aircraft.
      </p>
    </div>


<div className="component-grid">
  {/* Engine — available for 3D exploration */}
  <button
    className="component-card"
    onClick={() =>
      setSelectedModel({
        title: 'CFM56-5B Engine',
        path: '/models/engine/cfm56-5b.glb',
        scale: 1,
      })
    }
  >
    <div className="component-number">01</div>

    <div className="component-content">
      <p className="component-type">PROPULSION</p>

      <h3>CFM56-5B Engine</h3>

      <p>
        Explore one of the turbofan engines used
        across the A320 family in an interactive 3D view.
      </p>
    </div>

    <span className="component-arrow">EXPLORE ↗</span>
  </button>

  {/* Future aircraft systems */}
  <div className="component-card coming-soon-card">
    <div className="component-number">02</div>

    <div className="component-content">
      <p className="component-type">UNDER DEVELOPMENT</p>

      <h3>Coming Soon</h3>

      <p>
        More interactive 3D aircraft systems are
        being prepared for AeroMind.
      </p>
    </div>

    <span className="component-arrow">IN DEVELOPMENT</span>
  </div>
</div>
  </section>

  
  <footer className="footer">
    <div className="logo">AEROMIND</div>

    <p>AI-assisted aircraft exploration.</p>
  </footer>

  {isExplorerOpen && (
    <div className="explorer-overlay">
      <div className="explorer-panel">
        <div className="explorer-header">
          <div>
            <p className="eyebrow">AEROMIND / TECHNICAL LIBRARY</p>
            <h2>A320 Technical Explorer</h2>
          </div>

          <button
            className="explorer-close"
            onClick={() => setIsExplorerOpen(false)}
            aria-label="Close Technical Explorer"
          >
            ×
          </button>
        </div>

        
<div className="explorer-content">
  <div className="explorer-intro">
    <p className="eyebrow">AIRCRAFT SYSTEMS / A320 FAMILY</p>
    <h3>Explore the aircraft.</h3>
    <p>
      Discover the major systems that make the Airbus A320
      operate, from propulsion to flight control.
    </p>
  </div>

  <div className="explorer-system-grid">
    <button className="explorer-system-card">
      <span className="system-number">01 / PROPULSION</span>
      <span className="system-icon">◈</span>
      <h3>Engine</h3>
      <p>CFM56-5B turbofan engine</p>
    </button>

    <div className="explorer-system-card">
      <span className="system-number">02 / FLIGHT DECK</span>
      <span className="system-icon">⌘</span>
      <h3>Cockpit</h3>
      <p>Flight displays and pilot controls</p>
    </div>

    <div className="explorer-system-card">
      <span className="system-number">03 / FLIGHT CONTROL</span>
      <span className="system-icon">↗</span>
      <h3>Flight controls</h3>
      <p>Surfaces that control aircraft movement</p>
    </div>

    <div className="explorer-system-card">
      <span className="system-number">04 / STRUCTURE</span>
      <span className="system-icon">◇</span>
      <h3>Airframe & wings</h3>
      <p>Structure, lift and aerodynamic design</p>
    </div>

    <div className="explorer-system-card">
      <span className="system-number">05 / LANDING</span>
      <span className="system-icon">⇩</span>
      <h3>Landing gear</h3>
      <p>Ground support and landing mechanisms</p>
    </div>

    <div className="explorer-system-card">
      <span className="system-number">06 / AIRCRAFT SYSTEMS</span>
      <span className="system-icon">◎</span>
      <h3>Hydraulics</h3>
      <p>Power transmission for aircraft systems</p>
    
    </div>
  </div>

  

  {/* NEW: Single button to show or hide the image */}
  
<div className="systems-image-section">
  <button
    className="systems-image-button"
    onClick={() => setShowSystemsImage(true)}
  >
    View Aircraft Systems <span>↗</span>
  </button>
</div>
</div>

      </div>
    </div>

  )}
  
  {showSystemsImage && (
    <div
      className="systems-image-overlay"
      onClick={() => setShowSystemsImage(false)}
    >
      <button
        className="systems-image-close"
        onClick={() => setShowSystemsImage(false)}
        aria-label="Close image"
      >
        ×
      </button>

      <img
        src="/images/a320-infographic.png"
        alt="Airbus A320 aircraft systems infographic"
        className="systems-fullscreen-image"
        onClick={(event) => event.stopPropagation()}
      />
    </div>
  )}

  
{selectedModel && (
  <div
    className="model-viewer-overlay"
    onClick={() => setSelectedModel(null)}
  >
    <div
      className="model-viewer-window"
      onClick={(event) => event.stopPropagation()}
    >
      <div className="model-viewer-header">
        <div>
          <p className="eyebrow">AEROMIND / A320 FAMILY</p>
          <h2>{selectedModel.title}</h2>
          <p>Drag to rotate · Scroll to zoom</p>
        </div>

        <button
          className="model-viewer-close"
          onClick={() => setSelectedModel(null)}
          aria-label="Close 3D viewer"
        >
          ×
        </button>
      </div>

      <div className="model-viewer-canvas">
        <ModelViewer
          modelPath={selectedModel.path}
          scale={selectedModel.scale}
        />
      </div>

      <div className="model-viewer-footer">
        <span>3D MODEL VIEWER</span>
        <span>INTERACTIVE EXPLORATION</span>
      </div>
    </div>
  </div>
)}


      </main>
    )}
  </>
)
}

export default App
