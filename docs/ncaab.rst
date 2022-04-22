NCAAB Documentation
===================

The NCAAB package provides a module that allows the user to provide the
``year`` and ``level`` based on what the user would like.


Levels
======
This designates what the user would like to look at. If the user would like
to extract networks of teams for the given sport, then the user would
input ``level='team'``. Conversely, if the user would like to input at the
player level, the user would then input ``level='player'``.

Team
----

.. code-block:: python

    from epsn.ncaab import NCAAB
    import networkx as nx
    
    year = 2021
    team_output = NCAAB(year = year, level = 'team')
    response = team_output.response
    graph = nx.parse_gml(response['result'], label = 'id')

Player
------
Unfortunately, as of writing this documentation on 4/22/2022, there is no 
support at the player level. You will recieve ``null`` responses.