import pytest

from obugs.graphql.schema import schema
from obugs.backend import get_context
from obugs.settings import Settings


@pytest.fixture()
def database_setup():
    """Prepare a mock application to run REST tests"""
    settings = Settings()
    settings.database_uri = "sqlite:///:memory:"


@pytest.fixture()
async def context():
    """Define the context used by the graphql application"""
    context = await get_context()
    return context


@pytest.mark.asyncio
async def test_users(database_setup, context):
    """Test the execution of the querry qa"""
    
    query = """
        query TestQuery($search: String) {
            users(search: $search) {
                id
            }
        }
    """

    result = await schema.execute(
        query,
        context_value=context,
        variable_values={
            "search": None
        },
    )

    assert result.errors is None
    assert len(result.data["users"]) >= 0
