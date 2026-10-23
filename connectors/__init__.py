"""Connector adapters.

Skills ask for logical operations ("list campaigns", "update ad set budget");
adapters say which installed backend serves that operation and which tool to
call. Swapping a backend means editing one adapter, not every skill.
"""
