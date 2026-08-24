import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import createStudentApplication from '@salesforce/apex/StudentApplicationController.createStudentApplication';

export default class StudentApplicationForm extends LightningElement {
    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track program = 'Computer Science';
    @track applicationDate = '';
    @track notes = '';
    @track isLoading = false;

    get programOptions() {
        return [
            { label: 'Computer Science', value: 'Computer Science' },
            { label: 'Business Administration', value: 'Business Administration' },
            { label: 'Engineering', value: 'Engineering' },
            { label: 'Data Science', value: 'Data Science' },
            { label: 'Healthcare Management', value: 'Healthcare Management' }
        ];
    }

    handleInputChange(event) {
        const field = event.target.dataset.id;
        if (field === 'firstName') {
            this.firstName = event.target.value;
        } else if (field === 'lastName') {
            this.lastName = event.target.value;
        } else if (field === 'email') {
            this.email = event.target.value;
        } else if (field === 'phone') {
            this.phone = event.target.value;
        } else if (field === 'program') {
            this.program = event.target.value;
        } else if (field === 'applicationDate') {
            this.applicationDate = event.target.value;
        } else if (field === 'notes') {
            this.notes = event.target.value;
        }
    }

    handleClear() {
        this.firstName = '';
        this.lastName = '';
        this.email = '';
        this.phone = '';
        this.program = 'Computer Science';
        this.applicationDate = '';
        this.notes = '';
    }

    handleSubmit() {
        const allValid = [...this.template.querySelectorAll('lightning-input, lightning-combobox, lightning-textarea')]
            .reduce((validSoFar, inputFields) => {
                inputFields.reportValidity();
                return validSoFar && inputFields.checkValidity();
            }, true);

        if (!allValid) {
            this.showToast('Error', 'Please complete all required fields.', 'error');
            return;
        }

        this.isLoading = true;

        createStudentApplication({
            firstName: this.firstName,
            lastName: this.lastName,
            email: this.email,
            phone: this.phone,
            program: this.program,
            notes: this.notes
        })
        .then((recordId) => {
            this.isLoading = false;
            this.showToast('Success', 'Student Application submitted successfully! Record ID: ' + recordId, 'success');
            this.handleClear();
        })
        .catch((error) => {
            this.isLoading = false;
            const message = error.body && error.body.message ? error.body.message : error.message;
            this.showToast('Error Submitting Application', message, 'error');
        });
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