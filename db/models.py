import datetime as dt
from sqlalchemy import DateTime, ForeignKey, String, Interval
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Tracking(Base):
    __tablename__ = 'trackings'
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255))
    interval: Mapped[dt.timedelta] = mapped_column(Interval)
    save_all_screenshots: Mapped[bool]
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    web_page_states: Mapped[list['WebPageState']] = relationship(
        back_populates='tracking', passive_deletes=True
    )

    def __repr__(self) -> str:
        return f'Tracking(id={self.id!r}, url={self.url!r}, interval={self.interval!r}, created_at={self.created_at!r})'

    def __str__(self) -> str:
        return f'{self.url!s}'


class WebPageState(Base):
    __tablename__ = 'web_page_states'
    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_id: Mapped[int] = mapped_column(
        ForeignKey('trackings.id', ondelete='CASCADE')
    )
    tracking: Mapped[Tracking] = relationship(back_populates='web_page_states')
    image_filename: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f'WebPageState(id={self.id!r}, tracking={self.tracking!r}, image_filename={self.image_filename!r}, time={self.created_at!r})'

    def __str__(self) -> str:
        return f'{self.tracking!s} at {self.created_at!s}'
