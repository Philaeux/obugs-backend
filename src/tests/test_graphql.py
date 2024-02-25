import pytest

from obugs.graphql.schema import schema
from obugs.backend import get_context


@pytest.fixture()
async def context():
    """Define the context used by the graphql application"""
    context = await get_context()
    return context


@pytest.mark.asyncio
async def test_users(context):
    """Test the execution of the querry qa"""
    
    query = """
        query TestQuery {
            users {
                id
            }
        }
    """

    result = await schema.execute(
        query,
        context_value=context,
        variable_values={},
    )

    assert result.errors is None
    assert len(result.data["users"]) >= 0
