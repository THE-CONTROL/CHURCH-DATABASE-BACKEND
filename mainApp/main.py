from fastapi import FastAPI
from mainApp.data.all_database import group_models, event_models, single_models, group_members_models
from mainApp.data.database import engine
from mainApp.routers.single_route import admin, member, elder
from mainApp.routers.group_route import congregation, cottage, district, ministry
from mainApp.routers.event_route import baptism, communion_service, confirmation, service
from mainApp.routers.group_member_route import baptism_participants, communion_participants, \
    confirmation_participants, ministry_members
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(member.router)
app.include_router(elder.router)
app.include_router(congregation.router)
app.include_router(cottage.router)
app.include_router(district.router)
app.include_router(ministry.router)
app.include_router(baptism.router)
app.include_router(communion_service.router)
app.include_router(confirmation.router)
app.include_router(service.router)
app.include_router(baptism_participants.router)
app.include_router(confirmation_participants.router)
app.include_router(communion_participants.router)
app.include_router(ministry_members.router)

group_models.Base.metadata.create_all(engine)
event_models.Base.metadata.create_all(engine)
single_models.Base.metadata.create_all(engine)
group_members_models.Base.metadata.create_all(engine)
