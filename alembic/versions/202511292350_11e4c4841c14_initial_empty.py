"""initial empty

Revision ID: 11e4c4841c14
Revises:
Create Date: 2025-11-29 23:50:08.432076

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "11e4c4841c14"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 前処理
    pre_upgrade()
    pass
    # 後処理
    post_upgrade()


def downgrade() -> None:
    """Downgrade schema."""
    # 前処理
    pre_downgrade()
    pass
    # 後処理
    post_downgrade()


def pre_upgrade() -> None:
    # スキーマ更新前に実行する必要がある処理
    pass


def post_upgrade() -> None:
    # スキーマ更新後に実行する必要がある処理
    pass


def pre_downgrade() -> None:
    # スキーマ更新前に実行する必要がある処理
    pass


def post_downgrade() -> None:
    # スキーマ更新後に実行する必要がある処理
    pass
