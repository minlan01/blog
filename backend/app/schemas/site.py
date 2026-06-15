from pydantic import BaseModel, Field


class SiteProfile(BaseModel):
    site_name: str
    hero_title: str
    hero_subtitle: str
    intro_text: str
    avatar: str
    email: str
    github_url: str
    location: str
    icp_filing: str = ""
    icp_link: str = ""

    model_config = {"from_attributes": True}


class SiteProfileUpdate(BaseModel):
    site_name: str | None = Field(default=None, max_length=120)
    hero_title: str | None = Field(default=None, max_length=255)
    hero_subtitle: str | None = Field(default=None, max_length=255)
    intro_text: str | None = None
    avatar: str | None = Field(default=None, max_length=500)
    email: str | None = Field(default=None, max_length=120)
    github_url: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=120)
    icp_filing: str | None = Field(default=None, max_length=120)
    icp_link: str | None = Field(default=None, max_length=255)
