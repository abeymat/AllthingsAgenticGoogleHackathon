import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class StudentApplicationForm extends LightningElement {
    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track selectedProgram = '';
    @track tuitionAmount = 0;
    @track paymentMethod = 'Credit Card';
    @track isLoading = false;

    programOptions = [
        { label: 'Computer Science - $5,000', value: 'Computer Science', fee: 5000 },
        { label: 'Business Administration - $4,500', value: 'Business Administration', fee: 4500 },
        { label: 'Data Science - $5,500', value: 'Data Science', fee: 5500 },
        { label: 'Engineering - $6,000', value: 'Engineering', fee: 6000 }
    ];

    paymentMethodOptions = [
        { label: 'Credit Card', value: 'Credit Card' },
        { label: 'Bank Transfer', value: 'Bank Transfer' },
        { label: 'Financial Aid / Scholarship', value: 'Financial Aid' }
    ];

    handleInputChange(event) {
        const field = event.target.name;
        if (field === 'firstName') {
            this.firstName = event.target.value;
        } else if (field === 'lastName') {
            this.lastName = event.target.value;
        } else if (field === 'email') {
            this.email = event.target.value;
        } else if (field === 'phone') {
            this.phone = event.target.value;
        } else if (field === 'paymentMethod') {
            this.paymentMethod = event.target.value;
        }
    }

    handleProgramChange(event) {
        this.selectedProgram = event.detail.value;
        const selectedOption = this.programOptions.find(opt => opt.value === this.selectedProgram);
        if (selectedOption) {
            this.tuitionAmount = selectedOption.fee;
        }
    }

    handleSubmit() {
        if (!this.validateForm()) {
            this.showToast('Error', 'Please complete all required fields.', 'error');
            return;
        }

        this.isLoading = true;

        // Simulate form submission & payment processing
        setTimeout(() => {
            this.isLoading = false;
            this.showToast('Success', 'Student registration and tuition payment submitted successfully!', 'success');
            this.resetForm();
        }, 1200);
    }

    validateForm() {
        const allValid = [...this.template.querySelectorAll('lightning-input, lightning-combobox')]
            .reduce((validSoFar, inputCmp) => {
                inputCmp.reportValidity();
                return validSoFar && inputCmp.checkValidity();
            }, true);
        return allValid;
    }

    resetForm() {
        this.firstName = '';
        this.lastName = '';
        this.email = '';
        this.phone = '';
        this.selectedProgram = '';
        this.tuitionAmount = 0;
        this.paymentMethod = 'Credit Card';
    }

    showToast(title, message, variant) {
        const event = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(event);
    }
}