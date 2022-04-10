from pydantic import BaseModel

class NFL(BaseModel):
    gml: str
    
    class Config:
        schema_extra = {
            "example": {
                "1980": """
                graph[
                  multigraph 1
                  directed 1
                  node[
                    id "Buffalo Bills"
                    label "Bills"
                    location "Buffalo"
                  ]
                  node[
                    id "Miami Dolphins"
                    label "Dolphins"
                    location "Miami"
                  ]
                  ...
                  edge[
                    source "Miami Dolphins"
                    target "Buffalo Bills"
                    source_score 7
                    target_score 17
                    week 1
                    year 1980
                    is_postseason "False"
                  ]
                  edge[
                    source "Tampa Bay Buccaneers"
                    target "Cincinnati Bengals"
                    source_score 17
                    target_score 12
                    week 1
                    year 1980
                    is_postseason "False"
                  ]
                  ...
                ]
                    """}
        }


class NFLResponse(BaseModel):
    status: int
    gml: NFL