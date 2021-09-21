from dataclasses import dataclass
from typing import List

import locale

locale.setlocale(locale.LC_ALL, "")


@dataclass
class TaxBracket:
    income_limit: float
    tax_rate: float


@dataclass
class TaxCredits:
    # Non-Refundable Personal Tax Credits
    basic_personal_amount: float


@dataclass
class Tax:
    province: str
    tax_credits: TaxCredits
    tax_brackets: List[TaxBracket]

    @property
    def total_tax_credit(self) -> float:
        return self.tax_credits.basic_personal_amount * self.tax_brackets[0].tax_rate


# For tax brackets
# https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/canadian-income-tax-rates-individuals-current-previous-years.html
#
# 2021 Non-Refundable Personal Tax Credits - Base Amounts
# https://www.taxtips.ca/nrcredits/tax-credits-2021-base.htm#tax-credits-other-provinces

federal = Tax(
    province="Federal",
    tax_credits=TaxCredits(
        basic_personal_amount=13229  # TODO: 2020 value, to be updated
    ),
    tax_brackets=[
        TaxBracket(income_limit=0, tax_rate=0.15),
        TaxBracket(income_limit=49020, tax_rate=0.205),
        TaxBracket(income_limit=98040, tax_rate=0.26),
        TaxBracket(income_limit=151978, tax_rate=0.29),
        TaxBracket(income_limit=216511, tax_rate=0.33),
    ],
)


british_columbia = Tax(
    province="British Columbia",
    tax_credits=TaxCredits(basic_personal_amount=11070),
    tax_brackets=[
        TaxBracket(income_limit=0, tax_rate=5.06 / 100),
        TaxBracket(income_limit=42185, tax_rate=7.70 / 100),
        TaxBracket(income_limit=84370, tax_rate=10.50 / 100),
        TaxBracket(income_limit=96867, tax_rate=12.29 / 100),
        TaxBracket(income_limit=117624, tax_rate=14.70 / 100),
        TaxBracket(income_limit=159484, tax_rate=16.80 / 100),
        TaxBracket(income_limit=222421, tax_rate=20.5 / 100),
    ],
)

quebec = Tax(
    province="Quebec",
    tax_credits=TaxCredits(basic_personal_amount=15532),
    tax_brackets=[
        TaxBracket(income_limit=0, tax_rate=15.00 / 100),
        TaxBracket(income_limit=45105, tax_rate=20.00 / 100),
        TaxBracket(income_limit=90200, tax_rate=24.00 / 100),
        TaxBracket(income_limit=109755, tax_rate=25.75 / 100),
    ],
)

ontario = Tax(
    province="Ontario",
    tax_credits=TaxCredits(basic_personal_amount=10880),
    tax_brackets=[
        TaxBracket(income_limit=0, tax_rate=5.05 / 100),
        TaxBracket(income_limit=45142, tax_rate=9.15 / 100),
        TaxBracket(income_limit=90287, tax_rate=11.16 / 100),
        TaxBracket(income_limit=150000, tax_rate=12.16 / 100),
        TaxBracket(income_limit=220000, tax_rate=13.16 / 100),
    ],
)

alberta = Tax(
    province="Ontario",
    tax_credits=TaxCredits(basic_personal_amount=19369),
    tax_brackets=[
        TaxBracket(income_limit=0, tax_rate=10 / 100),
        TaxBracket(income_limit=128145, tax_rate=12 / 100),
        TaxBracket(income_limit=153773, tax_rate=13 / 100),
        TaxBracket(income_limit=205031, tax_rate=14 / 100),
        TaxBracket(income_limit=307547, tax_rate=15 / 100),
    ],
)


def income_tax(income: float, tax: Tax) -> float:
    amount = 0
    previous = TaxBracket(income_limit=0, tax_rate=0)
    for bracket in tax.tax_brackets:
        if income <= bracket.income_limit:
            break
        amount += (income - bracket.income_limit) * (
            bracket.tax_rate - previous.tax_rate
        )
        previous = bracket

    return max(0, amount - tax.total_tax_credit)


def total_income_tax(income: float, provincial: Tax) -> float:
    return sum(
        income_tax(income=income, tax=bracket) for bracket in [provincial, federal]
    )


readme = open("README.md", "w")


def println(line: str):
    readme.write(f"{line}")

    if line.startswith("#"):
        readme.write("\n\n")
    else:
        readme.write("\n")


println("# Canada Tax Brackets")

println(
    "If you are making $x per year, how much tax would you pay if you are living Vancouver, Toronto, Montreal, or Edmonton? "
)
println("")


def currency(amount: float):
    return locale.currency(amount, symbol=True, grouping=True)


city_and_provincial_tax = [
    ("Vancouver", british_columbia),
    ("Edmonton", alberta),
    ("Montreal", quebec),
    ("Toronto", ontario),
]

income = 100000
income_formated = currency(income)
println(f"If you are making {income_formated} per year, you would pay ...")

for city, tax in city_and_provincial_tax:
    tax_amount = total_income_tax(income=income, provincial=tax)
    tax_formated = currency(tax_amount)

    provincial_amount = income_tax(income=income, tax=tax)
    federal_tax_amount = income_tax(income=income, tax=federal)
    after_tax_amount = income - federal_tax_amount - provincial_amount

    println(f" + {tax_formated} of tax in {city}")
    println(f"   -  Provincial: {currency(provincial_amount)}")
    println(f"   -  Federal: {currency(federal_tax_amount)}")
    println(f"   -  After tax income: {currency(after_tax_amount)}")

println("")

readme.close()
