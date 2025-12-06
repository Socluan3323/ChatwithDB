from sqlalchemy import create_engine, Integer, String, select, update, delete, ForeignKey
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, Session, relationship
from typing import Optional, Dict, List


DB_URL = "postgresql+psycopg://postgres:Strongpassword1234@localhost:5432/shopdb"

engine = create_engine(DB_URL, echo=True, future=True)
Base = declarative_base()

def get_session():
    return Session(engine)

def init_schema():
    Base.metadata.create_all(engine)
    
    
    
class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"extend_existing":True }
    id: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    type_id: Mapped[str] = mapped_column(ForeignKey("product_types.id"))
    product_type: Mapped["ProductType"] = relationship(back_populates="products")
    extend_existing =True
    def __repr__(self) ->str: 
        return f"Product(id={self.id!r}) ,  name={self.name!r}, price={self.price!r})"


class ProductType(Base):
    __tablename__ = "product_types"
    __table_args__ = {"extend_existing":True }
    id: Mapped[int] = mapped_column(String(4), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    products: Mapped[List["Product"]] = relationship(
    back_populates="product_type",  
    lazy="selectin",  
    cascade="all, delete-orphan"
    
    )
    extend_existing =True
    def __repr__(self) ->str: 
        return f"Product(id={self.id!r}) ,  name={self.name!r})"
    def to_dict(self) -> Dict[str, int | str]:
        return {"name": self.name, "id": self.id}

 

def get_list_products():
    with Session(engine) as s:
        return [ p for p in s.scalars( select(Product)) ]
    
def get_product(product_id: int,engine) -> Optional[Product]:
    with Session(engine) as s:
        return s.get(Product,product_id)

def delete_product(product_id: int) -> int:
    with Session(engine) as s:
        result = s.execute(delete(Product).where(Product.id == product_id))
        s.commit()
        
def get_list_productTypes():
        with Session(engine) as s:
            return [ p for p in s.scalars( select(ProductType)) ]


def insert_one_product(p : Product):
    with Session(engine) as session:
        session.add(p)
        session.commit()

def insert_list_products(list: List[Product]):
    with Session(engine) as session:
        session.add_all(list)
        session.commit()
        
        
        