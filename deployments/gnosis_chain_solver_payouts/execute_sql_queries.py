import os
import logging
import pandas as pd

from sqlalchemy import create_engine
from dotenv import load_dotenv
from gnosis_chain_solver_payouts.constants import (
    UPPER_PERFORMANCE_REWARD_CAP,
    LOWER_PERFORMANCE_REWARD_CAP,
)

from gnosis_chain_solver_payouts.queries import (
        AUCTION_RANGE,
        QUOTE_REWARDS,
        SOLVER_REWARDS,
        SUCCESSFUL_AUCTION_IDS,
        PARTICIPATION_REWARDS_AUX,
)


logger = logging.getLogger(__name__)


def create_db_connections():
    """Helper function that creates the connections to the prod and barn db."""

    load_dotenv()
    barn_db_url = os.environ["BARN_DB_URL"]
    prod_db_url = os.environ["PROD_DB_URL"]
    barn_connection = create_engine(f"postgresql+psycopg2://{barn_db_url}")
    prod_connection = create_engine(f"postgresql+psycopg2://{prod_db_url}")

    return prod_connection, barn_connection


def get_auction_range(start_block_str, end_block_str, auction_range=AUCTION_RANGE):
    """
    Executes a query that returns the auction range between
    a start and an end block for prod and barn.
    """

    prod_connection, barn_connection = create_db_connections()

    """
    query_file = (
        open("gnosis_chain_solver_payouts/queries/auction_range.sql", "r")
        .read()
    )
    """
    auction_range = auction_range.replace("{{start_block}}", start_block_str)
    auction_range = auction_range.replace("{{end_block}}", end_block_str)

    with prod_connection.connect() as conn:
        res = pd.read_sql(auction_range, conn.connection)
    prod_start_auction_str = str(res["start_auction"].iloc[0])
    prod_end_auction_str = str(res["end_auction"].iloc[0])

    with barn_connection.connect() as conn:
        res = pd.read_sql(auction_range, conn.connection)
    barn_start_auction_str = str(res["start_auction"].iloc[0])
    barn_end_auction_str = str(res["end_auction"].iloc[0])

    return (
        prod_start_auction_str,
        prod_end_auction_str,
        barn_start_auction_str,
        barn_end_auction_str,
    )


def compute_quote_rewards(start_block_str, end_block_str, quote_rewards=QUOTE_REWARDS):
    """
    Executes a query that computes the number of quotes that should
    be rewarded, for each solver.
    """

    prod_connection, barn_connection = create_db_connections()

    quote_rewards = quote_rewards.replace("{{start_block}}", start_block_str)
    quote_rewards = quote_rewards.replace("{{end_block}}", end_block_str)

    results = []

    with prod_connection.connect() as conn:
        results.append(pd.read_sql(quote_rewards, conn.connection))
    with barn_connection.connect() as conn:
        results.append(pd.read_sql(quote_rewards, conn.connection))

    return pd.concat(results)


def compute_solver_rewards(start_block_str, end_block_str, solver_rewards=SOLVER_REWARDS):
    """Executes the main solver rewards query."""

    prod_connection, barn_connection = create_db_connections()

    solver_rewards = solver_rewards.replace("{{start_block}}", start_block_str)
    solver_rewards = solver_rewards.replace("{{end_block}}", end_block_str)
    solver_rewards = solver_rewards.replace("{{EPSILON_LOWER}}", str(LOWER_PERFORMANCE_REWARD_CAP))
    solver_rewards = solver_rewards.replace("{{EPSILON_UPPER}}", str(UPPER_PERFORMANCE_REWARD_CAP))
    results = []

    with prod_connection.connect() as conn:
        results.append(pd.read_sql(solver_rewards, conn.connection))
    with barn_connection.connect() as conn:
        results.append(pd.read_sql(solver_rewards, conn.connection))

    return pd.concat(results)


def execute_participation_rewards_helper(
        start_block_str,
        end_block_str,
        successful_auction_ids=SUCCESSFUL_AUCTION_IDS,
        participation_rewards_aux=PARTICIPATION_REWARDS_AUX,
):
    """
    Executes a helper query that recovers competition data, in order to be able
    to find the ranking and give weighted participation rewards.
    """

    prod_connection, barn_connection = create_db_connections()

    successful_auction_ids = successful_auction_ids.replace("{{start_block}}", start_block_str)
    successful_auction_ids = successful_auction_ids.replace("{{end_block}}", end_block_str)


    with prod_connection.connect() as conn:
        prod_res = pd.read_sql(successful_auction_ids, conn.connection)
    with barn_connection.connect() as conn:
        barn_res = pd.read_sql(successful_auction_ids, conn.connection)

    prod_auction_list = []
    barn_auction_list = []
    for index, row in prod_res.iterrows():
        prod_auction_list.append(str(row["auction_id"]))
    for index, row in barn_res.iterrows():
        barn_auction_list.append(str(row["auction_id"]))

    prod_auction_list_str = str(prod_auction_list).replace("[", "(").replace("]", ")")
    barn_auction_list_str = str(barn_auction_list).replace("[", "(").replace("]", ")")
    prod_pr_aux = participation_rewards_aux.replace("{{auction_list}}", prod_auction_list_str)
    barn_pr_aux = participation_rewards_aux.replace("{{auction_list}}", barn_auction_list_str)
    results = []
    if len(prod_auction_list) > 0:
        with prod_connection.connect() as conn:
            results.append(pd.read_sql(prod_pr_aux, conn.connection))
    if len(barn_auction_list) > 0:
        with barn_connection.connect() as conn:
            results.append(pd.read_sql(barn_pr_aux, conn.connection))

    return pd.concat(results)
