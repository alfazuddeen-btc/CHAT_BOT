import { useState, useEffect, useRef } from "react";

const API_URL = "http://127.0.0.1:8000";

const translations = {
  en: {
    title: "Medical Assistant",
    endSession: "End Session",
    noConversations: "No conversations yet. Start by asking a medical question.",
    you: "YOU",
    medicalAssistant: "MEDICAL ASSISTANT",
    placeholder: "Ask your medical question...",
    sending: "Sending...",
    send: "Send",
  },
  hi: {
    title: "चिकित्सा सहायक",
    endSession: "सत्र समाप्त करें",
    noConversations: "अभी तक कोई बातचीत नहीं। चिकित्सा प्रश्न पूछकर शुरू करें।",
    you: "आप",
    medicalAssistant: "चिकित्सा सहायक",
    placeholder: "अपना चिकित्सा प्रश्न पूछें...",
    sending: "भेज रहे हैं...",
    send: "भेजें",
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

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const loadChatHistory = async () => {
    const user_id = localStorage.getItem("user_id");

    if (!user_id) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/chat/history/user/${user_id}`);

      if (response.ok) {
        const data = await response.json();

        const previousMessages = [];
        data.messages.forEach((msg) => {
          previousMessages.push({ sender: "user", text: msg.message });
          previousMessages.push({ sender: "bot", text: msg.response });
        });

        setMessages(previousMessages);
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    } finally {
      setLoading(false);
    }
  };

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

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: localStorage.getItem("name"),
          dob: localStorage.getItem("dob"),
          pin: localStorage.getItem("pin"),
          session_id: localStorage.getItem("session_id"),
          message: currentInput,
          language: language,
        }),
      });

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
        <h2 style={{ margin: 0, fontSize: "1.8rem" }}>{t.title}</h2>

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
        {messages.length === 0 ? (
          <p style={{ textAlign: "center", color: "#999", padding: "3rem" }}>
            {t.noConversations}
          </p>
        ) : (
          messages.map((m, i) => (
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
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
              }}>
                {m.sender === "bot" ? (
                  <div dangerouslySetInnerHTML={{ __html: formatBotResponse(m.text) }} />
                ) : (
                  <div style={{ fontSize: "1rem", lineHeight: "1.6" }}>{m.text}</div>
                )}
              </div>
            </div>
          ))
        )}

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

        .formatted-response p {
          margin-bottom: 1rem;
          line-height: 1.7;
        }
        .formatted-response strong {
          display: block;
          font-weight: bold;
          font-size: 1.1em;
          margin: 1.2rem 0 0.5rem 0;
          color: #333;
        }
        .formatted-response ul {
          margin: 0.8rem 0;
          padding-left: 1.5rem;
        }
        .formatted-response li {
          margin-bottom: 0.5rem;
          line-height: 1.6;
        }
      `}</style>
    </div>
  );
}

export default Chat