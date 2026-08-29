import { LightningElement, track, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class StudentApplicationForm extends LightningElement {
    @api recordId;

    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track highSchool = '';
    @track gpa = '';
    @track programOfInterest = '';
    @track personalStatement = '';
    @track isSubmitting = false;

    get programOptions() {
        return [
            { label: 'Computer Science & Software Engineering', value: 'CS' },
            { label: 'Business Administration & Finance', value: 'BUS' },
            { label: 'Health & Life Sciences', value: 'HEALTH' },
            { label: 'Arts & Humanities', value: 'ARTS' },
            { label: 'Data Science & Artificial Intelligence', value: 'DS' }
        ];
    }

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
        } else if (field === 'highSchool') {
            this.highSchool = event.target.value;
        } else if (field === 'gpa') {
            this.gpa = event.target.value;
        } else if (field === 'programOfInterest') {
            this.programOfInterest = event.target.value;
        } else if (field === 'personalStatement') {
            this.personalStatement = event.target.value;
        }
    }

    handleSubmit(event) {
        if (event) {
            event.preventDefault();
        }

        const allValid = [...this.template.querySelectorAll('lightning-input, lightning-combobox, lightning-textarea')]
            .reduce((validSoFar, inputCmp) => {
                inputCmp.reportValidity();
                return validSoFar && inputCmp.checkValidity();
            }, true);

        if (!allValid) {
            this.showToast('Validation Error', 'Please complete all required fields correctly.', 'error');
            return;
        }

        this.isSubmitting = true;

        setTimeout(() => {
            this.isSubmitting = false;
            this.showToast(
                'Application Submitted!',
                `Thank you ${this.firstName}, your scholarship application has been successfully submitted.`,
                'success'
            );
            this.resetForm();
        }, 1000);
    }

    resetForm() {
        this.firstName = '';
        this.lastName = '';
        this.email = '';
        this.phone = '';
        this.highSchool = '';
        this.gpa = '';
        this.programOfInterest = '';
        this.personalStatement = '';
    }

    showToast(title, message, variant) {
        const evt = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(evt);
    }
}