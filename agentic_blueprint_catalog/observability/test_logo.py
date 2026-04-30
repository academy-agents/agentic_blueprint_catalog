from __future__ import annotations

from agentic_blueprint_catalog.observability.dashboard import Dashboard

dashboard = Dashboard()
x = dashboard._find_facility_logo(
    org='AS397511 Purdue University',
    fqdn='login3.frontera.tacc.utexas.edu',
)
print(x)
