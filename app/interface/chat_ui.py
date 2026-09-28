import html
import streamlit as st


def render_chat_message(role: str, content: str):
    """
    Render a clean custom chat bubble.

    User messages:
        Right aligned

    Assistant messages:
        Left aligned
    """

    # Escape HTML so user/document content cannot inject HTML.
    safe_content = html.escape(content)

    if role == "user":

        st.markdown(
            f"""
            <div class="chat-row user-row">
                <div class="chat-bubble user-bubble">
                    <div class="chat-label">You</div>
                    <div>{safe_content}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            f"""
            <div class="chat-row assistant-row">
                <div class="chat-bubble assistant-bubble">
                    <div class="chat-label">🤖 Assistant</div>
                    <div>{safe_content}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_chat_history():
    """
    Render all messages stored in session state.
    """

    chat_history = st.session_state.get("chat_history", [])

    for message in chat_history:

        render_chat_message(
            role=message["role"],
            content=message["content"],
        )
def load_chat_css():

    st.markdown(
        """
        <style>

        .chat-row {
            width: 100%;
            display: flex;
            margin: 12px 0;
        }

        .user-row {
            justify-content: flex-end;
        }

        .assistant-row {
            justify-content: flex-start;
        }

        .chat-bubble {
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 70%;
            line-height: 1.5;
            font-size: 15px;
            word-wrap: break-word;
        }

        .user-bubble {
            background: #DCF8C6;
            border-bottom-right-radius: 4px;
        }

        .assistant-bubble {
            background: #F1F3F5;
            border-bottom-left-radius: 4px;
        }

        .chat-label {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 5px;
            opacity: 0.65;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )