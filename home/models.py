from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.blocks import CharBlock, TextBlock, StructBlock, RichTextBlock, DateBlock, URLBlock
from wagtail.images.blocks import ImageChooserBlock
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.images.models import AbstractImage, AbstractRendition, Image


# ---------------------------------------------------------------------------
# Reusable StreamField Blocks
# ---------------------------------------------------------------------------

class SkillBlock(StructBlock):
    name = CharBlock(label="Skill name")
    level = CharBlock(label="Level", help_text="e.g. Expert, Intermediate, Beginner")

    class Meta:
        icon = "pick"


class ExperienceBlock(StructBlock):
    company = CharBlock()
    role = CharBlock()
    start_date = DateBlock()
    end_date = DateBlock(required=False, help_text="Leave blank if this is your current role")
    description = RichTextBlock(features=["bold", "italic", "ol", "ul"])

    class Meta:
        icon = "date"


class TechTagBlock(StructBlock):
    tag = CharBlock()

    class Meta:
        icon = "tag"


class CloudinaryImage(AbstractImage):
    admin_form_fields = Image.admin_form_fields

    def get_rendition(self, filter):
        rendition = super().get_rendition(filter)
        return rendition

    @property
    def default_alt_text(self):
        return self.title

    class Meta:
        verbose_name = 'Image'


class CloudinaryRendition(AbstractRendition):
    image = models.ForeignKey(
        CloudinaryImage,
        on_delete=models.CASCADE,
        related_name='renditions'
    )

    @property
    def url(self):
        # Use Cloudinary's transformation URL directly
        import cloudinary
        import cloudinary.utils
        # Extract the public_id from the original file
        public_id = self.image.file.name
        # Parse the filter to get dimensions
        filter_spec = self.filter_spec
        width = self.width
        height = self.height
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            width=width,
            height=height,
            crop="fill",
            secure=True
        )
        return url

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)

# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------

class HomePage(Page):
    image = models.ForeignKey(
        "home.CloudinaryImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Homepage image",
    )
    hero_text = models.CharField(
        blank=True,
        max_length=255,
        help_text="Write an introduction for the site",
    )
    hero_cta = models.CharField(
        blank=True,
        verbose_name="Hero CTA",
        max_length=255,
        help_text="Text to display on Call to Action",
    )
    hero_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Hero CTA link",
        help_text="Choose a page to link to for the Call to Action",
    )
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("hero_text"),
                FieldPanel("hero_cta"),
                FieldPanel("hero_cta_link"),
            ],
            heading="Hero section",
        ),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Home Page"


# ---------------------------------------------------------------------------
# About Page
# ---------------------------------------------------------------------------

class AboutPage(Page):
    photo = models.ForeignKey(
        "home.CloudinaryImage",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    bio = RichTextField(
        features=["bold", "italic", "link", "ol", "ul"],
        help_text="Write a bit about yourself",
    )
    cv_document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload your CV as a PDF so visitors can download it",
    )
    skills = StreamField(
        [("skill", SkillBlock())],
        blank=True,
        use_json_field=True,
        help_text="Add your skills one by one",
    )

    content_panels = Page.content_panels + [
        FieldPanel("photo"),
        FieldPanel("bio"),
        FieldPanel("cv_document"),
        FieldPanel("skills"),
    ]

    class Meta:
        verbose_name = "About Page"


# ---------------------------------------------------------------------------
# Experience Page
# ---------------------------------------------------------------------------

class ExperiencePage(Page):
    intro = models.TextField(
        blank=True,
        help_text="Optional intro sentence shown above your experience list",
    )
    experience = StreamField(
        [("job", ExperienceBlock())],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("experience"),
    ]

    class Meta:
        verbose_name = "Experience Page"


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectIndexPage(Page):
    intro = RichTextField(blank=True, help_text="Intro text shown above your projects grid")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["projects"] = (
            ProjectPage.objects.live().child_of(self).order_by("-first_published_at")
        )
        return context

    class Meta:
        verbose_name = "Projects Index"


class ProjectPage(Page):
    summary = models.CharField(max_length=255, help_text="One-line description shown on the projects grid")
    description = RichTextField(help_text="Full project description")
    thumbnail = models.ForeignKey(
        "home.CloudinaryImage",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    tech_stack = StreamField(
        [("tag", TechTagBlock())],
        blank=True,
        use_json_field=True,
        help_text="Add each technology used e.g. Python, React, PostgreSQL",
    )
    live_url = models.URLField(blank=True, help_text="Link to the live project")
    repo_url = models.URLField(blank=True, help_text="Link to the source code / GitHub repo")

    content_panels = Page.content_panels + [
        FieldPanel("summary"),
        FieldPanel("description"),
        FieldPanel("thumbnail"),
        FieldPanel("tech_stack"),
        MultiFieldPanel(
            [
                FieldPanel("live_url"),
                FieldPanel("repo_url"),
            ],
            heading="Links",
        ),
    ]

    class Meta:
        verbose_name = "Project"


# ---------------------------------------------------------------------------
# Contact Page  (Wagtail form — submissions saved in admin + emailed to you)
# ---------------------------------------------------------------------------

class ContactFormField(AbstractFormField):
    page = ParentalKey(
        "ContactPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class ContactPage(AbstractEmailForm):
    intro = RichTextField(blank=True, help_text="Text shown above the contact form")
    thank_you_text = RichTextField(blank=True, help_text="Shown after the form is submitted")

    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    email_address = models.EmailField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        FormSubmissionsPanel(),
        MultiFieldPanel(
            [
                FieldPanel("github_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("email_address"),
            ],
            heading="Social & contact links",
        ),
    ]

    class Meta:
        verbose_name = "Contact Page"