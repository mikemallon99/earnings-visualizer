import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"

from typing import List, Tuple
import yfinance as yf
import plotly.graph_objects as go


class Node:
    def __init__(
        self, name: str, pos: Tuple[float, float], amount: int, color: str = "green"
    ):
        self.name = name
        self.pos = pos
        self.color = color
        self.amount = amount


class Edge:
    def __init__(self, source: Node, target: Node, value: int):
        self.source = source
        self.target = target
        self.value = value


class Graph:
    def __init__(self, nodes: List[Node], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges


class OpExEntry:
    def __init__(self, name: str, amount: int):
        self.name = name
        self.amount = amount


class EarningsReport:
    def __init__(
        self,
        revenue,
        cogs,
        opex_total,
        op_rd,
        op_admin,
        pretax_income: int,
        income_tax: int,
    ):
        self.revenue: int = revenue
        self.cogs: int = cogs
        self.gross_profit: int = revenue - cogs
        self.op_rd: int = op_rd
        self.op_admin: int = op_admin
        self.opex_other: int = opex_total - op_rd - op_admin
        self.opex_total: int = opex_total
        self.op_income: int = self.gross_profit - self.opex_total
        self.pretax_income: int = pretax_income
        self.other_income: int = pretax_income - self.op_income
        self.income_tax: int = income_tax
        self.net_income: int = self.pretax_income - self.income_tax


def get_report_from_ticker(ticker: str):
    stock = yf.Ticker(ticker)
    financials = stock.quarterly_income_stmt
    latest_quarter = financials.iloc[:, 0]
    revenue = latest_quarter["Total Revenue"]
    cogs = latest_quarter["Cost Of Revenue"]
    # gross_profit = latest_quarter["Gross Profit"]
    opex = latest_quarter["Operating Expense"]
    rd_cost = latest_quarter.get("Research And Development", 0)
    admin_cost = latest_quarter.get("Selling General And Administration", 0)
    pretax_income = latest_quarter["Pretax Income"]
    income_tax = latest_quarter["Tax Provision"]
    return EarningsReport(
        revenue, cogs, opex, rd_cost, admin_cost, pretax_income, income_tax
    )


def get_node_by_name(node_list: List[Node], node_name: str):
    for node in node_list:
        if node.name == node_name:
            return node
    return None


def make_graph_from_report(report: EarningsReport) -> Graph:
    nodes = [
        Node("Revenue", (0.01, 0.5), report.revenue),
        Node("Cost of Revenue", (0.135, 0.7), report.cogs, "red"),
        Node("Gross Profit", (0.25, 0.4), report.gross_profit),
        Node("Operating Expenses", (0.385, 0.7), report.opex_total, "red"),
    ]
    edge_config = [
        ("Revenue", "Cost of Revenue", report.cogs),
        ("Revenue", "Gross Profit", report.gross_profit),
        ("Gross Profit", "Operating Expenses", report.opex_total),
    ]

    if report.op_rd > 0:
        nodes.append(Node("Research and Development", (0.5, 0.6), report.op_rd, "red"))
        edge_config.append(
            ("Operating Expenses", "Research and Development", report.op_rd)
        )

    if report.op_admin > 0:
        nodes.append(Node("Sales, General & Admin", (0.5, 0.8), report.op_admin, "red"))
        edge_config.append(
            ("Operating Expenses", "Sales, General & Admin", report.op_admin)
        )

    if report.opex_other > 0:
        nodes.append(Node("Other", (0.5, 0.9), report.opex_other, "red"))
        edge_config.append(("Operating Expenses", "Other", report.opex_other))

    nodes.append(Node("Operating Income", (0.5, 0.3), report.op_income))
    edge_config.append(("Gross Profit", "Operating Income", report.op_income))

    if report.other_income > 0:
        nodes.append(Node("Other Income", (0.6, 0.1), report.other_income))
        edge_config.append(("Other Income", "Pretax Income", report.other_income))

    nodes.append(Node("Pretax Income", (0.75, 0.2), report.pretax_income))
    edge_config.append(("Operating Income", "Pretax Income", report.op_income))

    if report.income_tax > 0:
        nodes.append(Node("Tax", (0.885, 0.4), report.income_tax, "red"))
        edge_config.append(("Pretax Income", "Tax", report.income_tax))
    else:
        nodes.append(Node("Tax (benefit)", (0.885, 0.4), -report.income_tax))
        edge_config.append(("Tax (benefit)", "Net Profit", -report.income_tax))

    nodes.append(Node("Net Profit", (0.99, 0.1), report.net_income))
    edge_config.append(("Pretax Income", "Net Profit", report.net_income))

    # Creating Edge instances using node names, getting node references by get_node_by_name
    edges = [
        Edge(get_node_by_name(nodes, start), get_node_by_name(nodes, end), weight) if weight > 0 else Edge(get_node_by_name(nodes, start), get_node_by_name(nodes, end), 1)
        for start, end, weight in edge_config
    ]


    # change node color if negative
    for node in nodes:
        if node.color == 'green' and node.amount <= 0:
            node.color = 'red'

    return Graph(nodes, edges)


def format_dollar_amount(amount: int):
    # amount is measured in dollars
    if amount >= 1000000000 or amount <= -1000000000:
        return "${:.1f}B".format(amount / 1000000000)
    else:
        return "${:.0f}M".format(amount / 1000000)


def convert_graph_to_plotly(graph: Graph, title: str, out_path: str):
    # Extracting labels and assigning colors to nodes
    labels = [
        f"{node.name}<br>{format_dollar_amount(node.amount)}" for node in graph.nodes
    ]
    colors = ["#60c465" if node.color == "green" else "#c22f36" for node in graph.nodes]

    # Defining x coordinates for nodes. You might want to adapt these based on your specific data and use case.
    x_pos = [node.pos[0] for node in graph.nodes]
    y_pos = [node.pos[1] for node in graph.nodes]

    # Extracting source, target and value for edges
    source = [graph.nodes.index(edge.source) for edge in graph.edges]
    target = [graph.nodes.index(edge.target) for edge in graph.edges]
    link_colors = [
        "#92f7a8" if edge.target.color == "green" else "#fc7e85" for edge in graph.edges
    ]
    value = [edge.value for edge in graph.edges]

    # Create a Plotly Sankey diagram
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="fixed",
                node=dict(
                    pad=200,
                    thickness=20,
                    line=dict(color="black", width=0.0),
                    label=labels,
                    color=colors,
                    x=x_pos,
                    y=y_pos,
                ),
                textfont=dict(family="Arial, sans-serif", size=16, color="black"),
                link=dict(source=source, target=target, value=value, color=link_colors),
            )
        ]
    )

    fig.update_layout(
        title_text=title,
        font_size=15,
        width=1000,
        height=600,
        margin=dict(t=50, b=20, l=20, r=20),
    )
    fig.write_image(out_path)


def create_img_from_ticker(ticker):
    nvidia_report = get_report_from_ticker(ticker)
    nvidia_graph = make_graph_from_report(nvidia_report)
    img_path = "test.png"
    convert_graph_to_plotly(nvidia_graph, f"{ticker} Earnings Q2 2023", img_path)
    return img_path
