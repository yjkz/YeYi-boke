from pydantic import BaseModel


class SiteConfigResponse(BaseModel):
    site_title: str = "YeYi 的博客"
    site_subtitle: str = ""
    logo_url: str = ""
    favicon_url: str = ""
    about_content: str = ""
    footer_text: str = ""
    social_links: dict = {}
    comment_enabled: bool = True
    comment_need_review: bool = True

    model_config = {"from_attributes": True}


class SiteConfigUpdate(BaseModel):
    site_title: str | None = None
    site_subtitle: str | None = None
    logo_url: str | None = None
    favicon_url: str | None = None
    about_content: str | None = None
    footer_text: str | None = None
    social_links: dict | None = None
    comment_enabled: bool | None = None
    comment_need_review: bool | None = None


class AnnouncementResponse(BaseModel):
    content: str = ""
