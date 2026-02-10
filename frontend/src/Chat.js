import { useState, useEffect, useRef } from "react";

//const API_URL = "http://127.0.0.1:8000";
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const translations = {
  en: {
    title: "Medical Assistant",
    endSession: "End Session",
    you: "YOU",
    medicalAssistant: "MEDICAL ASSISTANT",
    placeholder: "Type your response...",
    sending: "Sending...",
    send: "Send",
    welcome: ` Welcome to Medical Assistant

I'm your intelligent medical assistant powered by AI. I can help you with:

 Medical questions and information
 Health advice and guidance
 Disease information and symptoms
 Wellness tips

 Important: I provide general medical information, not professional diagnosis. Always consult a doctor for serious concerns.

Before we proceed, I need your consent to store our conversation data.

 Consent Required

To continue, please provide your consent:

Your data will be:
- Stored securely in our encrypted database
- Used only for medical assistance
- Never shared with third parties

Type: "I agree" or "I consent"`,
  },
  hi: {
    title: "चिकित्सा सहायक",
    endSession: "सत्र समाप्त करें",
    you: "आप",
    medicalAssistant: "चिकित्सा सहायक",
    placeholder: "अपना उत्तर टाइप करें...",
    sending: "भेज रहे हैं...",
    send: "भेजें",
    welcome: ` चिकित्सा सहायक में आपका स्वागत है

मैं आपका AI-संचालित चिकित्सा सहायक हूं। मैं आपकी मदद कर सकता हूं:

 चिकित्सा प्रश्न और जानकारी
 स्वास्थ्य सलाह
 रोग की जानकारी
 स्वास्थ्य सुझाव

 महत्वपूर्ण: मैं सामान्य चिकित्सा जानकारी देता हूं, निदान नहीं। गंभीर समस्याओं के लिए हमेशा डॉक्टर से मिलें।

 सहमति आवश्यक

जारी रखने के लिए, कृपया सहमति दें:

आपका डेटा:
- हमारे एन्क्रिप्टेड डेटाबेस में सुरक्षित रूप से संग्रहीत
- केवल चिकित्सा सहायता के लिए उपयोग
- किसी से साझा नहीं किया जाएगा

टाइप करें: "सहमत हूं" या "मैं सहमत हूं"`,
  },
};

function Chat({ logout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState("en");
  const messagesEndRef = useRef(null);

  const t = translations[language];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadChatHistory = async () => {
    const token = localStorage.getItem("access_token");
    const user_id = localStorage.getItem("user_id");

    if (!token || !user_id) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/chat/history/user/${user_id}`, {
        headers: {
          "Authorization": `Bearer ${token}`  // Send JWT token
        }
      });

      if (response.status === 401) {
        // Token expired or invalid
        alert("Session expired. Please login again.");
        handleLogout();
        return;
      }

      if (response.ok) {
        const data = await response.json();

        if (data.messages.length === 0) {
          setMessages([{
            sender: "bot",
            text: t.welcome
          }]);
        } else {
          const previousMessages = [];
          data.messages.forEach((msg) => {
            previousMessages.push({ sender: "user", text: msg.message });
            previousMessages.push({ sender: "bot", text: msg.response });
          });
          setMessages(previousMessages);
        }
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const formatBotResponse = (text) => {
    let formatted = text;
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/^\* (.*?)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*?<\/li>\n?)+/g, '<ul>$&</ul>');
    formatted = formatted.split('\n\n').map(para => {
      if (!para.includes('<ul>') && !para.includes('<li>')) {
        return `<p>${para.replace(/\n/g, '<br>')}</p>`;
      }
      return para;
    }).join('');
    return formatted;
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const token = localStorage.getItem("access_token");
    const session_id = localStorage.getItem("session_id");

    if (!token) {
      alert("Session expired. Please login again.");
      handleLogout();
      return;
    }

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          message: currentInput,
          session_id: session_id,
          language: language,
        }),
      });

      if (res.status === 401) {
        alert("Session expired. Please login again.");
        handleLogout();
        return;
      }

      if (!res.ok) {
        throw new Error("Failed to send message");
      }

      const data = await res.json();
      setMessages((prev) => [...prev, { sender: "bot", text: data.response }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { sender: "bot", text: "Error: Unable to process request." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    logout();
  };

  if (loading) {
    return <div style={{ padding: "2rem", textAlign: "center" }}>Loading...</div>;
  }

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "20px" }}>

      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "20px",
        borderBottom: "2px solid #333",
        paddingBottom: "15px"
      }}>
        <h2 style={{ margin: 0, fontSize: "1.8rem" }}>
          {t.title}
          <span style={{ fontSize: "0.7rem", color: "#666", marginLeft: "10px" }}>
             Secured with JWT
          </span>
        </h2>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: "4px",
              border: "2px solid #0066cc",
              background: "#fff",
              cursor: "pointer",
              fontWeight: "bold",
              color: "#0066cc"
            }}
          >
            <option value="en">English</option>
            <option value="hi">हिंदी</option>
          </select>

          <button onClick={handleLogout} style={{
            padding: "10px 20px",
            background: "#000",
            color: "#fff",
            border: "2px solid #000",
            cursor: "pointer",
            borderRadius: "4px"
          }}>
            {t.endSession}
          </button>
        </div>
      </div>

      <div style={{
        maxHeight: "600px",
        overflowY: "auto",
        marginBottom: "20px",
        padding: "10px"
      }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            marginBottom: "30px",
            display: "flex",
            flexDirection: "column",
            alignItems: m.sender === "user" ? "flex-end" : "flex-start"
          }}>

            <div style={{
              fontSize: "0.75rem",
              fontWeight: "bold",
              textTransform: "uppercase",
              color: m.sender === "user" ? "#0066cc" : "#00aa00",
              marginBottom: "8px",
              letterSpacing: "1px"
            }}>
              {m.sender === "user" ? t.you : t.medicalAssistant}
            </div>

            <div style={{
              maxWidth: "85%",
              padding: "15px 20px",
              borderRadius: "12px",
              background: m.sender === "user" ? "#e3f2fd" : "#f5f5f5",
              border: m.sender === "user" ? "2px solid #0066cc" : "2px solid #ddd",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              wordWrap: "break-word"
            }}>
              {m.sender === "bot" ? (
                <div dangerouslySetInnerHTML={{ __html: formatBotResponse(m.text) }} />
              ) : (
                <div style={{ fontSize: "1rem", lineHeight: "1.6" }}>{m.text}</div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{
            marginBottom: "30px",
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start"
          }}>
            <div style={{
              fontSize: "0.75rem",
              fontWeight: "bold",
              textTransform: "uppercase",
              color: "#00aa00",
              marginBottom: "8px",
              letterSpacing: "1px"
            }}>
              {t.medicalAssistant}
            </div>

            <div style={{
              maxWidth: "85%",
              padding: "15px 20px",
              borderRadius: "12px",
              background: "#f5f5f5",
              border: "2px solid #ddd",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}>
              <span style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#0066cc",
                animation: "pulse 1.5s infinite"
              }}></span>
              <span style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#0066cc",
                animation: "pulse 1.5s infinite 0.2s"
              }}></span>
              <span style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#0066cc",
                animation: "pulse 1.5s infinite 0.4s"
              }}></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isLoading && sendMessage()}
          placeholder={t.placeholder}
          disabled={isLoading}
          style={{
            flex: 1,
            padding: "15px",
            fontSize: "1rem",
            border: "2px solid #ddd",
            borderRadius: "8px",
            opacity: isLoading ? 0.6 : 1,
            cursor: isLoading ? "not-allowed" : "text"
          }}
        />
        <button onClick={sendMessage} disabled={isLoading} style={{
          padding: "15px 30px",
          background: isLoading ? "#ccc" : "#0066cc",
          color: "#fff",
          border: "none",
          borderRadius: "8px",
          cursor: isLoading ? "not-allowed" : "pointer",
          fontWeight: "bold",
          fontSize: "1rem"
        }}>
          {isLoading ? t.sending : t.send}
        </button>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }
      `}</style>
    </div>
  );
}

export default Chat;
