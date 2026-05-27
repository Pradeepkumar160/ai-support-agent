"""
Tool implementations — no OpenAI needed for core tools.
FAQ search uses a simple keyword fallback if no embeddings available.
"""
from sqlalchemy.orm import Session
from app.models.all_models import Order, Ticket

# Simple FAQ list — no embeddings needed, works without any API key
FAQS = [
    ("refund", "Refunds take 5-7 business days to process back to your original payment method."),
    ("track", "You can track your orders using the order ID. Try asking: Track my order #101"),
    ("support", "Our customer support team is available 24/7 via chat and email."),
    ("return", "We offer a 30-day return policy for all unused items in their original packaging."),
    ("shipping", "Shipping typically takes 3-5 business days for standard domestic orders."),
    ("express", "Express shipping is available at checkout and arrives within 1-2 business days."),
    ("international", "International shipping usually takes 10-14 business days."),
    ("cancel", "You can cancel your order within 1 hour of placing it if it has not shipped yet."),
    ("damaged", "Damaged or defective items can be replaced at no cost — contact support with a photo."),
    ("gift", "Gift cards are non-refundable but never expire."),
]


def lookup_order(order_id_str: str, db: Session) -> str:
    try:
        order_id = int(str(order_id_str).strip())
    except (ValueError, AttributeError):
        return "Error: order_id must be a number. Example: 101"

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return f"No order found with ID {order_id}. Please check the order number."

    return (
        f"Order #{order.id}: '{order.item_name}' — Status: {order.status} "
        f"(Customer: {order.customer_email})"
    )


def create_support_ticket(description: str, db: Session, subject: str = "User Support Request", customer_email: str = "") -> str:
    ticket = Ticket(
        subject=subject,
        description=description,
        status="OPEN",
        customer_email=customer_email,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return f"Support ticket #{ticket.id} created successfully with status OPEN."


def search_faq(query: str) -> str:
    """Keyword-based FAQ search — works without any API key."""
    query_lower = query.lower()
    matches = []
    for keyword, answer in FAQS:
        if keyword in query_lower:
            matches.append(answer)
    if not matches:
        # Return top 2 generic answers
        matches = [FAQS[0][1], FAQS[4][1]]
    return "FAQ Results:\n" + "\n".join(f"- {m}" for m in matches[:3])
