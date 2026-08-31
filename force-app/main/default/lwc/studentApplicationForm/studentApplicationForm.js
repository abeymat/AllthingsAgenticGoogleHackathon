import { LightningElement, track, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import submitApplication from '@salesforce/apex/StudentApplicationController.submitApplication';

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

        if (!this.firstName || !this.lastName || !this.email) {
            this.showToast('Validation Error', 'Please complete all required fields.', 'error');
            return;
        }

        this.isSubmitting = true;

        submitApplication({ firstName: this.firstName, lastName: this.lastName, email: this.email })
            .then(result => {
                this.isSubmitting = false;
                this.showToast(
                    'Application Submitted!',
                    `Thank you ${this.firstName}, your application has been created (Contact ID: ${result}).`,
                    'success'
                );
                this.resetForm();
            })
            .catch(error => {
                this.isSubmitting = false;
                const msg = error && error.body ? error.body.message : JSON.stringify(error);
                this.showToast('Error Submitting Application', msg, 'error');
            });
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