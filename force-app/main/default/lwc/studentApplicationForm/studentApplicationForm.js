import { LightningElement, track, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class StudentApplicationForm extends LightningElement {
    @api recordId;
    @track isLoading = false;

    @track formData = {
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        program: '',
        tuitionAmount: null,
        semester: '',
        paymentMethod: ''
    };

    get programOptions() {
        return [
            { label: 'Computer Science', value: 'CS' },
            { label: 'Business Administration', value: 'BA' },
            { label: 'Data Science', value: 'DS' },
            { label: 'Health Sciences', value: 'HS' }
        ];
    }

    get semesterOptions() {
        return [
            { label: 'Fall 2024', value: 'Fall 2024' },
            { label: 'Spring 2025', value: 'Spring 2025' },
            { label: 'Summer 2025', value: 'Summer 2025' }
        ];
    }

    get paymentOptions() {
        return [
            { label: 'Credit Card', value: 'Credit Card' },
            { label: 'ACH / Direct Debit', value: 'ACH' },
            { label: 'Tuition Installment Plan', value: 'Installment' }
        ];
    }

    handleInputChange(event) {
        const field = event.target.dataset.field;
        if (field) {
            this.formData = {
                ...this.formData,
                [field]: event.target.value
            };
        }
    }

    validateInputs() {
        const allValid = [
            ...this.template.querySelectorAll('lightning-input, lightning-combobox')
        ].reduce((validSoFar, inputCmp) => {
            inputCmp.reportValidity();
            return validSoFar && inputCmp.checkValidity();
        }, true);

        return allValid;
    }

    async handleSubmit(event) {
        event.preventDefault();

        if (!this.validateInputs()) {
            this.showNotification(
                'Validation Error',
                'Please complete all required fields with valid values.',
                'error'
            );
            return;
        }

        this.isLoading = true;

        try {
            // Emulate asynchronous registration and payment processing
            await new Promise((resolve) => setTimeout(resolve, 1000));

            this.showNotification(
                'Success',
                'Registration and tuition details submitted successfully.',
                'success'
            );

            this.handleReset();
        } catch (error) {
            this.showNotification(
                'Submission Error',
                error.body ? error.body.message : error.message || 'An unexpected error occurred.',
                'error'
            );
        } finally {
            this.isLoading = false;
        }
    }

    handleReset() {
        this.formData = {
            firstName: '',
            lastName: '',
            email: '',
            phone: '',
            program: '',
            tuitionAmount: null,
            semester: '',
            paymentMethod: ''
        };

        const inputs = this.template.querySelectorAll('lightning-input, lightning-combobox');
        inputs.forEach((input) => {
            input.value = null;
        });
    }

    showNotification(title, message, variant) {
        const toastEvt = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(toastEvt);
    }
}