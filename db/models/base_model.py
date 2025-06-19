from sqlalchemy import inspect
from config.logger import logger
from config.postgres import db_session
from datetime import datetime, timezone
from sqlalchemy import func, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm.exc import DetachedInstanceError

Base = declarative_base()

class BaseModel(Base):
	__abstract__ = True

	def __getattribute__(self, name):
		"""Override attribute access to provide better error messages for lazy loading"""
		try:
			return super().__getattribute__(name)
		except DetachedInstanceError as e:
			# Check if this is a relationship attribute
			if hasattr(self.__class__, name):
				attr = getattr(self.__class__, name)
				if hasattr(attr.property, 'mapper'):  # It's a relationship
					# Create a more helpful error message
					class_name = self.__class__.__name__
					primary_key_name = inspect(self.__class__).primary_key[0].name
					primary_key_value = getattr(self, primary_key_name, 'unknown')

					helpful_msg = (
						f"Cannot lazy load '{name}' on {class_name} - session was closed!\n"
						f"This happens when:\n"
						f"   • You call close_session() and then try to access relationships\n"
						f"   • The object was created in a different request/task\n"
						f"   • Session timeout occurred\n"
						f"Solutions:\n"
						f"   • Access relationships BEFORE calling close_session()\n"
						f"   • Use eager loading with db_session.query({class_name}).options(joinedload())\n"
						f"   • Re-query the object: {class_name}.find('{primary_key_value}')\n"
						f"Original error: {str(e)}"
					)

					# Log the helpful message
					logger.error(helpful_msg)

					# Raise the original error with enhanced message
					raise DetachedInstanceError(helpful_msg) from e

			# Re-raise original error if not a relationship
			raise

	@classmethod
	def create_record(cls, fields):
		"""Create a new record."""
		try:
			if not fields: raise OperationalError("Parameter 'fields' cannot be empty")

			obj = cls(**fields)
			db_session.add(obj)
			db_session.commit()
			db_session.refresh(obj)
			return obj
		except SQLAlchemyError as e:
			db_session.rollback()
			logger.error(f"SQLAlchemy error: {e}", exc_info=True)
			return False
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	@classmethod
	def fetch_record_by_id(cls, record_id):
		"""Find a record by its ID."""
		try:
			if not record_id: raise OperationalError("Parameter 'record_id' cannot be empty")

			return db_session.query(cls).get(record_id)
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	@classmethod
	def fetch_records(cls, filters=None):
		"""Find all records by a filter."""
		try:
			filters = filters or {}
			return db_session.query(cls).filter_by(**filters).all()
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	@classmethod
	def count(cls, filters=None):
		"""Count records by a filter."""
		try:
			filters = filters or {}
			pk_column = inspect(cls).primary_key[0]
			return db_session.query(func.count(pk_column)).filter_by(**filters).scalar()
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	@classmethod
	def first(cls, count=1):
		"""Fetch the first records by the given count."""
		try:
			pk_column = inspect(cls).primary_key[0]
			query = db_session.query(cls).order_by(asc(pk_column)).limit(count)
			return query.first() if count == 1 else query.all()
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	@classmethod
	def last(cls, count=1):
		"""Fetch the last records by the given count."""
		try:
			pk_column = inspect(cls).primary_key[0]
			query = db_session.query(cls).order_by(desc(pk_column)).limit(count)
			return query.first() if count == 1 else query.all()
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	@classmethod
	def update_records(cls, filters, fields):
		"""Update records matching the filter with new values."""
		try:
			if not fields: raise OperationalError("Parameter 'fields' cannot be empty")

			fields['updated_at'] = datetime.now(timezone.utc)

			result = db_session.query(cls).filter_by(**filters).update(fields)
			db_session.commit()
			return result
		except SQLAlchemyError as e:
			db_session.rollback()
			logger.error(f"SQLAlchemy error: {e}", exc_info=True)
			return False
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	def update_attributes(self, fields):
		"""Update specific fields of the current instance."""
		try:
			if not fields: raise OperationalError("Parameter 'fields' cannot be empty")

			fields['updated_at'] = datetime.now(timezone.utc)

			for key, value in fields.items():
				setattr(self, key, value)
			db_session.add(self)
			db_session.commit()
			db_session.refresh(self)
			return self
		except SQLAlchemyError as e:
			db_session.rollback()
			logger.error(f"SQLAlchemy error: {e}", exc_info=True)
			return False
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	def destroy(self):
		"""Delete current instance (ActiveRecord-style)"""
		try:
			db_session.delete(self)
			db_session.commit()
			return True
		except SQLAlchemyError as e:
			db_session.rollback()
			logger.error(f"SQLAlchemy error: {e}", exc_info=True)
			return False
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	@classmethod
	def delete_records(cls, filters):
		"""Delete records matching the filter."""
		try:
			result = db_session.query(cls).filter_by(**filters).delete()
			db_session.commit()
			return result
		except SQLAlchemyError as e:
			db_session.rollback()
			logger.error(f"SQLAlchemy error: {e}", exc_info=True)
			return False
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False

	def to_dict(self):
		"""Convert the instance to a dictionary representation."""
		try:
			return { column.name: getattr(self, column.name) for column in self.__table__.columns }
		except Exception as e:
			logger.error(f"Error: {e}", exc_info=True)
			return False
