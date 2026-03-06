"""init tables

Revision ID: f5f9fd8c86be
Revises: 
Create Date: 2026-03-07 01:41:07.663803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5f9fd8c86be'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создаёт начальную схему demo-приложения."""
    op.create_table(
        "users",
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_tg_id"), "users", ["tg_id"], unique=True)

    op.create_table(
        "game_sessions",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "game_type",
            sa.Enum("hilo", "dice", name="game_type_enum", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("bet_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("last_message_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending_start",
                "active",
                "won",
                "lost",
                "cancelled",
                name="game_session_status_enum",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("win_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_win", sa.Boolean(), nullable=True),
        sa.Column("is_bonus", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_sessions_user_tg_id"),
        "game_sessions",
        ["user_tg_id"],
        unique=False,
    )

    op.create_table(
        "game_settings",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("bet_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_settings_user_tg_id"),
        "game_settings",
        ["user_tg_id"],
        unique=True,
    )

    op.create_table(
        "wallet_balances",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_wallet_balances_user_tg_id"),
        "wallet_balances",
        ["user_tg_id"],
        unique=True,
    )

    op.create_table(
        "transactions",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 4), nullable=False),
        sa.Column(
            "type",
            sa.Enum("debit", "credit", name="transaction_type_enum", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column(
            "reason",
            sa.Enum(
                "deposit",
                "withdraw_check",
                "withdraw_transfer",
                "game_loss",
                "game_win",
                "bonus_game_win",
                "referral",
                "bonus",
                "cashback",
                "bet",
                name="transaction_reason_enum",
                native_enum=False,
                length=30,
            ),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index(
        op.f("ix_transactions_user_tg_id"),
        "transactions",
        ["user_tg_id"],
        unique=False,
    )

    op.create_table(
        "deposit_invoices",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 4), nullable=False),
        sa.Column("provider_invoice_id", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "paid",
                "expired",
                name="deposit_invoice_status_enum",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_deposit_invoices_provider_invoice_id"),
        "deposit_invoices",
        ["provider_invoice_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_deposit_invoices_user_tg_id"),
        "deposit_invoices",
        ["user_tg_id"],
        unique=False,
    )

    op.create_table(
        "game_hilo_details",
        sa.Column("game_session_id", sa.Integer(), nullable=False),
        sa.Column("first_dice_value", sa.Integer(), nullable=False),
        sa.Column("second_dice_value", sa.Integer(), nullable=False),
        sa.Column("roll_number", sa.Integer(), nullable=False),
        sa.Column("chosen_outcome", sa.String(length=10), nullable=True),
        sa.Column("multiplier", sa.Numeric(10, 2), nullable=False),
        sa.Column("cumulative_multiplier", sa.Numeric(10, 2), nullable=False),
        sa.Column("win_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_win", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["game_session_id"], ["game_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_hilo_details_game_session_id"),
        "game_hilo_details",
        ["game_session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Удаляет начальную схему demo-приложения."""
    op.drop_index(op.f("ix_game_hilo_details_game_session_id"), table_name="game_hilo_details")
    op.drop_table("game_hilo_details")

    op.drop_index(op.f("ix_deposit_invoices_user_tg_id"), table_name="deposit_invoices")
    op.drop_index(
        op.f("ix_deposit_invoices_provider_invoice_id"),
        table_name="deposit_invoices",
    )
    op.drop_table("deposit_invoices")

    op.drop_index(op.f("ix_transactions_user_tg_id"), table_name="transactions")
    op.drop_table("transactions")

    op.drop_index(op.f("ix_wallet_balances_user_tg_id"), table_name="wallet_balances")
    op.drop_table("wallet_balances")

    op.drop_index(op.f("ix_game_settings_user_tg_id"), table_name="game_settings")
    op.drop_table("game_settings")

    op.drop_index(op.f("ix_game_sessions_user_tg_id"), table_name="game_sessions")
    op.drop_table("game_sessions")

    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.drop_table("users")
