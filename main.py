from typing import List, Tuple
import plotly.graph_objects as go


nvidia_data = {
    "revenue": 20699,
    "cost_of_revenue": 6589,
    "gross_profit": 14110,
    "operating_expenses": {
        "research_and_development": 3916,
        "sales_and_administration": 1253,
    },
    "operating_income": 8941,
    "income_pretax": 9190,
    "income_tax_expense": 958,
    "net_income": 958,

}

class Node:
    def __init__(self, name: str, pos: Tuple[float, float], amount: int, color: str="green"):
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
    def __init__(self, revenue, cogs, opex: List[OpExEntry], pretax_income: int, income_tax: int):
        self.revenue: int = revenue
        self.cogs: int = cogs
        self.gross_profit: int = revenue - cogs
        self.opex: List[OpExEntry] = opex
        self.opex_total: int = sum(entry.amount for entry in opex)
        self.op_income: int = self.gross_profit - self.opex_total
        self.pretax_income: int = pretax_income
        self.other_income: int = pretax_income - self.op_income
        self.income_tax: int = income_tax
        self.net_income: int = self.pretax_income - self.income_tax


def make_graph_from_report(report: EarningsReport) -> Graph:
    nodes = [
        Node("Revenue", (0, 0), report.revenue),
        Node("Cost of Revenue", (0.135, 0.7), report.cogs, "red"),
        Node("Gross Profit", (0.25, 0.4), report.gross_profit),
        Node("Operating Expenses", (0.385, 0.7), report.opex_total, "red"),
        # Node("Research and Development"),
        # Node("Sales, General & Admin"),
        Node("Operating Income", (0.5, 0.3), report.op_income),
        Node("Other Income", (0.6, 0.1), report.other_income),
        Node("Pretax Income", (0.75, 0.2), report.pretax_income),
        Node("Tax", (0.885, 0.4), report.income_tax, "red"),
        Node("Net Profit", (1, 0.1), report.net_income),
    ]
    edges = [
        Edge(nodes[0], nodes[1], report.cogs),
        Edge(nodes[0], nodes[2], report.gross_profit),
        Edge(nodes[2], nodes[3], report.opex_total),
        Edge(nodes[2], nodes[4], report.op_income),
        Edge(nodes[4], nodes[6], report.op_income),
        Edge(nodes[5], nodes[6], report.other_income),
        Edge(nodes[6], nodes[7], report.income_tax),
        Edge(nodes[6], nodes[8], report.net_income),
    ]
    for i, entry in enumerate(report.opex):
        if len(report.opex) == 1:
            nodes.append(Node(entry.name, (0.5, (0.7 + .1)), entry.amount, "red"))
        else:
            nodes.append(Node(entry.name, (0.5, (0.7 - .1) + (i/(len(report.opex)-1)) * 0.2), entry.amount, "red"))
        edges.append(Edge(nodes[3], nodes[-1], entry.amount))

    return Graph(nodes, edges)


def format_dollar_amount(amount: int):
    # amount is measured in millions
    if amount >= 1000:
        return "${:.1f}B".format(amount / 1000)
    else:
        return "${:.0f}M".format(amount)



def convert_graph_to_plotly(graph: Graph, title: str):
    # Extracting labels and assigning colors to nodes
    labels = [f"{node.name}<br>{format_dollar_amount(node.amount)}" for node in graph.nodes]
    colors = ["#60c465" if node.color == 'green' else '#c22f36' for node in graph.nodes]

    # Defining x coordinates for nodes. You might want to adapt these based on your specific data and use case.
    x_pos = [node.pos[0] for node in graph.nodes]
    y_pos = [node.pos[1] for node in graph.nodes]
    
    # Extracting source, target and value for edges
    source = [graph.nodes.index(edge.source) for edge in graph.edges]
    target = [graph.nodes.index(edge.target) for edge in graph.edges]
    link_colors = ["#92f7a8" if edge.target.color == 'green' else '#fc7e85' for edge in graph.edges]
    value = [edge.value for edge in graph.edges]

    # Create a Plotly Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=200,
            thickness=20,
            line=dict(color="black", width=0.0),
            label=labels,
            color=colors,
            x=x_pos,
            y=y_pos,
        ),
        textfont=dict(
            family="Arial, sans-serif",
            size=16,
            color="black"
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors
        ))])

    fig.update_layout(
        title_text=title, 
        font_size=15,
        width=1000,
        height=600,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    fig.show()

nvidia_opex = [
    OpExEntry("Research and Development", 3916),
    OpExEntry("Sales, General & Admin", 1253),
]
nvidia_report: EarningsReport = EarningsReport(revenue=20699, cogs=6589, opex=nvidia_opex, pretax_income=9190, income_tax=958)
nvidia_graph = make_graph_from_report(nvidia_report)
convert_graph_to_plotly(nvidia_graph, "NVIDIA Earnings Q2 2023")