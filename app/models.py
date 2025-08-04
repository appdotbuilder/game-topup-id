from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GameCategory(str, Enum):
    MOBA = "moba"
    BATTLE_ROYALE = "battle_royale"
    RPG = "rpg"
    FPS = "fps"
    STRATEGY = "strategy"
    OTHER = "other"


# Persistent models (stored in database)
class Game(SQLModel, table=True):
    """Represents popular games available for top-up."""

    __tablename__ = "games"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    slug: str = Field(max_length=100, unique=True, index=True)
    category: GameCategory = Field(default=GameCategory.OTHER)
    description: str = Field(default="", max_length=500)
    icon_url: Optional[str] = Field(default=None, max_length=255)
    banner_url: Optional[str] = Field(default=None, max_length=255)
    publisher: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    digiflazz_brand: str = Field(max_length=50)  # Brand code in Digiflazz API
    user_id_label: str = Field(default="User ID", max_length=50)  # Label for user ID input
    user_id_placeholder: str = Field(default="Enter your game User ID", max_length=100)
    user_id_help_text: Optional[str] = Field(default=None, max_length=200)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    products: List["Product"] = Relationship(back_populates="game")
    transactions: List["Transaction"] = Relationship(back_populates="game")


class Product(SQLModel, table=True):
    """Represents top-up denominations/products for games."""

    __tablename__ = "products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="games.id", index=True)
    digiflazz_sku: str = Field(max_length=50, unique=True, index=True)  # SKU in Digiflazz API
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=500)
    denomination: str = Field(max_length=100)  # e.g., "100 Diamonds", "1000 UC"
    price: Decimal = Field(decimal_places=2, max_digits=12)
    original_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    discount_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    category: str = Field(default="", max_length=50)  # e.g., "diamonds", "uc", "cp"
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    sort_order: int = Field(default=0)
    stock_status: str = Field(default="available", max_length=20)  # available, out_of_stock, limited
    minimum_purchase: int = Field(default=1, ge=1)
    maximum_purchase: int = Field(default=10, ge=1)
    processing_time: str = Field(default="1-5 minutes", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    game: Game = Relationship(back_populates="products")
    transaction_items: List["TransactionItem"] = Relationship(back_populates="product")


class Customer(SQLModel, table=True):
    """Represents customers making top-up purchases."""

    __tablename__ = "customers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, max_length=255, index=True)
    phone: Optional[str] = Field(default=None, max_length=20, index=True)
    name: Optional[str] = Field(default=None, max_length=100)
    is_registered: bool = Field(default=False)
    total_spent: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=12)
    total_transactions: int = Field(default=0, ge=0)
    last_transaction_at: Optional[datetime] = Field(default=None)
    preferred_payment_method: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="customer")


class Transaction(SQLModel, table=True):
    """Represents top-up transactions."""

    __tablename__ = "transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(max_length=100, unique=True, index=True)  # Our internal transaction ID
    digiflazz_ref_id: Optional[str] = Field(default=None, max_length=100, index=True)  # Digiflazz reference ID
    customer_id: Optional[int] = Field(default=None, foreign_key="customers.id", index=True)
    game_id: int = Field(foreign_key="games.id", index=True)
    game_user_id: str = Field(max_length=100)  # The user's game account ID
    game_user_server: Optional[str] = Field(default=None, max_length=50)  # For games with server selection
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, index=True)
    total_amount: Decimal = Field(decimal_places=2, max_digits=12)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    payment_reference: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)
    error_message: Optional[str] = Field(default=None, max_length=500)
    digiflazz_response: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    processed_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Optional[Customer] = Relationship(back_populates="transactions")
    game: Game = Relationship(back_populates="transactions")
    items: List["TransactionItem"] = Relationship(back_populates="transaction")


class TransactionItem(SQLModel, table=True):
    """Represents individual items in a transaction."""

    __tablename__ = "transaction_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id", index=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(decimal_places=2, max_digits=12)
    total_price: Decimal = Field(decimal_places=2, max_digits=12)
    digiflazz_sku: str = Field(max_length=50)  # Store SKU for reference
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transaction: Transaction = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="transaction_items")


class PaymentMethod(SQLModel, table=True):
    """Represents available payment methods."""

    __tablename__ = "payment_methods"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    slug: str = Field(max_length=50, unique=True, index=True)
    provider: str = Field(max_length=50)  # e.g., "digiflazz", "midtrans"
    type: str = Field(max_length=30)  # e.g., "bank_transfer", "e_wallet", "virtual_account"
    icon_url: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=200)
    min_amount: Decimal = Field(default=Decimal("1000"), decimal_places=2, max_digits=12)
    max_amount: Decimal = Field(default=Decimal("10000000"), decimal_places=2, max_digits=12)
    fee_percentage: Decimal = Field(default=Decimal("0"), decimal_places=4, max_digits=8)
    fee_fixed: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=12)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SystemConfig(SQLModel, table=True):
    """Stores system configuration and settings."""

    __tablename__ = "system_configs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(max_length=100, unique=True, index=True)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=200)
    is_secret: bool = Field(default=False)  # For sensitive config like API keys
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiLog(SQLModel, table=True):
    """Logs API calls to external services like Digiflazz."""

    __tablename__ = "api_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    service: str = Field(max_length=50, index=True)  # e.g., "digiflazz"
    endpoint: str = Field(max_length=200)
    method: str = Field(max_length=10)  # GET, POST, etc.
    request_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    response_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    status_code: Optional[int] = Field(default=None)
    response_time_ms: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=500)
    transaction_id: Optional[str] = Field(default=None, max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class GameCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    category: GameCategory = Field(default=GameCategory.OTHER)
    description: str = Field(default="", max_length=500)
    icon_url: Optional[str] = Field(default=None, max_length=255)
    banner_url: Optional[str] = Field(default=None, max_length=255)
    publisher: str = Field(max_length=100)
    digiflazz_brand: str = Field(max_length=50)
    user_id_label: str = Field(default="User ID", max_length=50)
    user_id_placeholder: str = Field(default="Enter your game User ID", max_length=100)
    user_id_help_text: Optional[str] = Field(default=None, max_length=200)
    sort_order: int = Field(default=0)


class GameUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    category: Optional[GameCategory] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=500)
    icon_url: Optional[str] = Field(default=None, max_length=255)
    banner_url: Optional[str] = Field(default=None, max_length=255)
    publisher: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)
    sort_order: Optional[int] = Field(default=None)


class ProductCreate(SQLModel, table=False):
    game_id: int
    digiflazz_sku: str = Field(max_length=50)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=500)
    denomination: str = Field(max_length=100)
    price: Decimal = Field(decimal_places=2, max_digits=12)
    original_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    discount_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    category: str = Field(default="", max_length=50)
    sort_order: int = Field(default=0)


class ProductUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    original_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    discount_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    is_active: Optional[bool] = Field(default=None)
    is_featured: Optional[bool] = Field(default=None)
    stock_status: Optional[str] = Field(default=None, max_length=20)
    sort_order: Optional[int] = Field(default=None)


class TransactionCreate(SQLModel, table=False):
    game_id: int
    game_user_id: str = Field(max_length=100)
    game_user_server: Optional[str] = Field(default=None, max_length=50)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    customer_name: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=500)


class TransactionItemCreate(SQLModel, table=False):
    product_id: int
    quantity: int = Field(ge=1)


class TopUpRequest(SQLModel, table=False):
    """Schema for top-up requests from the UI."""

    game_id: int
    product_id: int
    game_user_id: str = Field(max_length=100)
    game_user_server: Optional[str] = Field(default=None, max_length=50)
    quantity: int = Field(default=1, ge=1)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    customer_name: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)


class TransactionResponse(SQLModel, table=False):
    """Schema for transaction responses."""

    transaction_id: str
    status: TransactionStatus
    total_amount: Decimal
    message: str
    payment_url: Optional[str] = Field(default=None)
    estimated_completion: Optional[str] = Field(default=None)


class GameSummary(SQLModel, table=False):
    """Simplified game data for UI display."""

    id: int
    name: str
    slug: str
    category: GameCategory
    icon_url: Optional[str]
    banner_url: Optional[str]
    publisher: str
    user_id_label: str
    user_id_placeholder: str
    user_id_help_text: Optional[str]
    is_active: bool


class ProductSummary(SQLModel, table=False):
    """Simplified product data for UI display."""

    id: int
    digiflazz_sku: str
    name: str
    denomination: str
    price: Decimal
    original_price: Optional[Decimal]
    discount_percentage: Optional[int]
    category: str
    is_featured: bool
    stock_status: str
    processing_time: str


class TransactionSummary(SQLModel, table=False):
    """Simplified transaction data for UI display."""

    id: int
    transaction_id: str
    game_name: str
    game_user_id: str
    status: TransactionStatus
    total_amount: Decimal
    created_at: str  # ISO format string
    completed_at: Optional[str]  # ISO format string
