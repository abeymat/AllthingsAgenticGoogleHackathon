import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

/**
 * @description LWC Controller for handling student registration applications.
 */
export default class StudentApplicationForm extends LightningElement {
    @track formData = {
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        birthdate: '',
        program: '',
        comments: ''
    };

    isLoading = false;

    get programOptions() {
        return [
            { label: 'Computer Science', value: 'Computer Science' },
            { label: 'Business Administration', value: 'Business Administration' },
            { label: 'Engineering', value: 'Engineering' },
            { label: 'Arts & Humanities', value: 'Arts & Humanities' },
            { label: 'Data Science', value: 'Data Science' }
        ];
    }

    handleInputChange(event) {
        const field = event.target.dataset.field || event.target.name;
        if (field) {
            this.formData = {
                ...this.formData,
                [field]: event.target.value
            };
        }
    }

    handleReset() {
        this.formData = {
            firstName: '',
            lastName: '',
            email: '',
            phone: '',
            birthdate: '',
            program: '',
            comments: ''
        };
        const inputFields = this.template.querySelectorAll('lightning-input, lightning-combobox, lightning-textarea');
        if (inputFields) {
            inputFields.forEach(field => {
                field.value = '';
            });
        }
    }

    handleSubmit(event) {
        if (event) {
            event.preventDefault();
        }

        const allValid = [
            ...this.template.querySelectorAll('lightning-input, lightning-combobox, lightning-textarea')
        ].reduce((validSoFar, inputCmp) => {
            inputCmp.reportValidity();
            return validSoFar && inputCmp.checkValidity();
        }, true);

        if (!allValid) {
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Validation Error',
                    message: 'Please complete all required fields correctly before submitting.',
                    variant: 'error'
                })
            );
            return;
        }

        this.isLoading = true;

        // Process application submission logic
        setTimeout(() => {
            this.isLoading = false;
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Application Submitted',
                    message: 'Student application submitted successfully!',
                    variant: 'success'
                })
            );
            this.handleReset();
        }, 1000);
    }
}