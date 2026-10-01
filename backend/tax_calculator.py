class TaxCalculator:
    @staticmethod
    def calculate_tax(gross_pay: float) -> float:
        """
        Calculate taxes based on the following brackets:
        - Gross Pay <= 5000: 0% Tax
        - 5000 < Gross Pay <= 15000: 10% Tax
        - Gross Pay > 15000: 15% Tax

        Note: This is a simulation for a Diploma Task.
        """
        if gross_pay <= 5000:
            return 0.0
        if gross_pay <= 15000:
            return gross_pay * 0.10
        return gross_pay * 0.15

    @staticmethod
    def calculate_net_pay(gross_pay: float) -> float:
        """
        Calculate Net Pay: Gross Pay - Tax
        """
        tax = TaxCalculator.calculate_tax(gross_pay)
        return gross_pay - tax
