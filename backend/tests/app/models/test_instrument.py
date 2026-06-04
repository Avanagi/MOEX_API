"""
Тесты для Pydantic-моделей инструментов.
Проверяют валидацию, сериализацию, значения полей и ограничения.
"""
import pytest
from datetime import date, datetime

from app.models.instrument import InstrumentOut, InstrumentFilter, InstrumentSearch


class TestInstrumentOut:
    """Тесты модели InstrumentOut — ответ API с данными инструмента."""

    def test_create_instrument_out(self, sample_instrument_data):
        """Проверяет корректное создание InstrumentOut из словаря данных."""
        inst = InstrumentOut(**sample_instrument_data)
        assert inst.ticker == "SBER"
        assert inst.name == "Сбербанк"
        assert inst.type == "stock"
        assert inst.sector == "finance"
        assert inst.price == 250.5
        assert inst.volume == 1000000
        assert inst.currency == "RUB"
        assert inst.yield_ == 12.5
        assert inst.maturity_date == date(2030, 1, 1)
        assert inst.market_cap == 5000000000
        assert inst.issuer == "Сбербанк России"
        assert inst.volatility == 15.3
        assert inst.strike_price is None
        assert inst.option_type is None

    def test_instrument_out_with_optional_fields_none(self):
        """Проверяет создание InstrumentOut со всеми None для опциональных полей."""
        inst = InstrumentOut(
            ticker="TEST",
            name="Тест",
            type="stock",
            sector=None,
            price=None,
            volume=None,
            currency=None,
            updated_at=datetime.now(),
            yield_=None,
            maturity_date=None,
            market_cap=None,
            issuer=None,
            volatility=None,
            strike_price=None,
            option_type=None,
        )
        assert inst.ticker == "TEST"
        assert inst.sector is None
        assert inst.price is None

    def test_instrument_out_serialization(self, sample_instrument_data):
        """Проверяет сериализацию InstrumentOut в словарь (model_dump)."""
        inst = InstrumentOut(**sample_instrument_data)
        data = inst.model_dump(by_alias=True)
        assert data["ticker"] == "SBER"
        assert data["yield"] == 12.5

    def test_instrument_out_alias_yield(self, sample_instrument_data):
        """Проверяет что поле yield_ сериализуется как 'yield' (по alias)."""
        inst = InstrumentOut(**sample_instrument_data)
        data = inst.model_dump(by_alias=True)
        assert "yield" in data
        assert data["yield"] == 12.5
        assert "yield_" not in data


class TestInstrumentFilter:
    """Тесты модели InstrumentFilter — параметры фильтрации запроса."""

    def test_default_values(self):
        """Проверяет значения по умолчанию для всех полей фильтра."""
        filt = InstrumentFilter()
        assert filt.type is None
        assert filt.sector is None
        assert filt.min_price is None
        assert filt.max_price is None
        assert filt.sort_by == "ticker"
        assert filt.order == "asc"
        assert filt.limit == 50
        assert filt.offset == 0

    @pytest.mark.parametrize("valid_type", ["stock", "bond", "futures", "option"])
    def test_valid_type(self, valid_type):
        """Проверяетacceptance валидных типов инструментов."""
        filt = InstrumentFilter(type=valid_type)
        assert filt.type == valid_type

    def test_invalid_type_raises(self):
        """Проверяет что невалидный тип вызывает ошибку валидации."""
        with pytest.raises(Exception):
            InstrumentFilter(type="invalid")

    @pytest.mark.parametrize("valid_sort_by", ["ticker", "price", "volume", "name", "market_cap"])
    def test_valid_sort_by(self, valid_sort_by):
        """Проверяет accept валидных полей для сортировки."""
        filt = InstrumentFilter(sort_by=valid_sort_by)
        assert filt.sort_by == valid_sort_by

    def test_invalid_sort_by_raises(self):
        """Проверяет что невалидное поле сортировки вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(sort_by="invalid")

    @pytest.mark.parametrize("valid_order", ["asc", "desc"])
    def test_valid_order(self, valid_order):
        """Проверяет accept валидных направлений сортировки."""
        filt = InstrumentFilter(order=valid_order)
        assert filt.order == valid_order

    def test_invalid_order_raises(self):
        """Проверяет что невалидное направление сортировки вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(order="invalid")

    def test_min_price_ge_zero(self):
        """Проверяет что min_price >= 0 валидируется корректно."""
        filt = InstrumentFilter(min_price=0)
        assert filt.min_price == 0

    def test_min_price_negative_raises(self):
        """Проверяет что отрицательная min_price вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(min_price=-1)

    def test_max_price_ge_zero(self):
        """Проверяет что max_price >= 0 валидируется корректно."""
        filt = InstrumentFilter(max_price=100)
        assert filt.max_price == 100

    def test_max_price_negative_raises(self):
        """Проверяет что отрицательная max_price вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(max_price=-1)

    def test_min_yield_ge_zero(self):
        """Проверяет что min_yield >= 0 валидируется корректно."""
        filt = InstrumentFilter(min_yield=0)
        assert filt.min_yield == 0

    def test_min_yield_negative_raises(self):
        """Проверяет что отрицательная min_yield вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(min_yield=-1)

    def test_max_yield_ge_zero(self):
        """Проверяет что max_yield >= 0 валидируется корректно."""
        filt = InstrumentFilter(max_yield=100)
        assert filt.max_yield == 100

    def test_max_yield_negative_raises(self):
        """Проверяет что отрицательная max_yield вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(max_yield=-1)

    def test_limit_within_range(self):
        """Проверяет что limit в диапазоне [1, 200] проходит валидацию."""
        filt = InstrumentFilter(limit=1)
        assert filt.limit == 1
        filt = InstrumentFilter(limit=200)
        assert filt.limit == 200

    def test_limit_too_low_raises(self):
        """Проверяет что limit < 1 вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(limit=0)

    def test_limit_too_high_raises(self):
        """Проверяет что limit > 200 вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(limit=201)

    def test_offset_ge_zero(self):
        """Проверяет что offset >= 0 валидируется корректно."""
        filt = InstrumentFilter(offset=0)
        assert filt.offset == 0

    def test_offset_negative_raises(self):
        """Проверяет что отрицательный offset вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentFilter(offset=-1)

    def test_maturity_dates(self):
        """Проверяет установку дат срока погашения."""
        filt = InstrumentFilter(
            maturity_from=date(2024, 1, 1),
            maturity_to=date(2025, 12, 31),
        )
        assert filt.maturity_from == date(2024, 1, 1)
        assert filt.maturity_to == date(2025, 12, 31)


class TestInstrumentSearch:
    """Тесты модели InstrumentSearch — параметры текстового поиска."""

    def test_valid_search_query(self):
        """Проверяет корректную валидацию строки поиска."""
        search = InstrumentSearch(q="SBER")
        assert search.q == "SBER"

    def test_empty_query_raises(self):
        """Проверяет что пустая строка поиска вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentSearch(q="")

    def test_max_length_query(self):
        """Проверяет что строка длиной 100 символов проходит валидацию."""
        search = InstrumentSearch(q="a" * 100)
        assert len(search.q) == 100

    def test_too_long_query_raises(self):
        """Проверяет что строка длиной 101 символ вызывает ошибку."""
        with pytest.raises(Exception):
            InstrumentSearch(q="a" * 101)
